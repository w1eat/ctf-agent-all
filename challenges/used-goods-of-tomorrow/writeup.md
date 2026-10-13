# Used Goods of Tomorrow 题解

- 分类：web
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

Come to Tommorow-Mart for all your used goods! We even have a partnership with FutureBank to grant you 500 free credits to start!

## 解题原理

该题是一道 GraphQL API 越权与业务逻辑组合漏洞题。服务端在 /graphql 上开启内省，并把一个本应仅内部/维护使用的 mutation vendorTerminalSync 遗留在了线上（描述中自述为 closed beta 期间 Left enabled）。该 mutation 无任何鉴权即可返回 VendorDiagnostics，其中包含厂商主密钥 vendorKey。攻击者用泄露的 vendorKey 作为参数查询 promoCodes，即可读到内部促销表，获得 FOUNDERS-100（对 Lot #4042 打 100% 折扣、标注 Internal use only）。最终把该促销码用于 placeOrder 下单 Lot #4042：该商品（Founders Vault Deed，SEALED）标价 1,000,000 信用点，而新账号仅有 500 信用点；由于折扣把价格算成 0，绕过了余额限制完成购买，回执中的 flag 字段返回 sun{1_l0v3_fr33_stuff}。核心成因是隐藏的敏感 mutation 未鉴权暴露、内部促销码未做权限校验、服务端对下单价格的计算完全信任客户端传入的 promoCode。

## 关键步骤

1. 枚举 GraphQL 接口：向目标 /graphql 端点发送内省查询（如 {__schema{...}}），发现除公开字段外还存在隐藏的内部变更 vendorTerminalSync(terminalId: ID)，其返回类型 VendorDiagnostics 含 vendorKey 字段，描述中自称 INTERNAL / MAINTENANCE、从 closed beta 遗留启用。
2. 无需任何鉴权调用该 mutation：mutation{vendorTerminalSync{terminalId status firmware vendorKey note}}，响应中直接返回厂商主密钥 vendorKey=VND-MASTER-21d5f80206dffb6fa9ad5722。
3. 以泄露的 vendorKey 作为参数查询促销表：{promoCodes(vendorKey:"VND-MASTER-21d5f80206dffb6fa9ad5722"){code description percentOff appliesTo}}，得到包括 FOUNDERS-100 在内的折扣数据，其描述为 100% off Lot #4042. Internal use only.，appliesTo=4042。
4. 确认目标商品：listing 4042（Founders Vault Deed，SEALED）的 priceCredits=1,000,000，而新注册账号只发放 500 信用点，正常途径无法购买。
5. 注册账号后以下单 mutation 购买该商品：mutation($id:ID!,$promo:String){placeOrder(listingId:$id,promoCode:$promo){success message listingId pricePaid flag}}，传 id=4042、promoCode=FOUNDERS-100；返回 success=true、pricePaid=0，说明 100% 折扣把应付价格降为 0，绕过信用点余额限制。
6. 读取回执中的 flag 字段，得到 sun{1_l0v3_fr33_stuff}。

## EXP 与运行方法

文件：无

材料中 exp_files 为空，replay.status 为 manual，即没有可自动运行的 EXP 脚本，只能按题解步骤人工复现：使用 GraphQL 客户端（或向 /graphql 发 POST 请求）依次手工构造并发送上述四条请求（内省枚举、无鉴权调用 vendorTerminalSync、带 vendorKey 的 promoCodes 查询、带 promoCode=FOUNDERS-100 的 placeOrder），并观察每步响应字段。故无法声称 EXP 已自动复现，也没有可用的命令行、退出码或标准输出。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- GraphQL endpoint /graphql with introspection exposes an internal mutation vendorTerminalSync (description: 'INTERNAL / MAINTENANCE ... Left enabled from the closed beta').
- Calling `mutation{vendorTerminalSync{terminalId status firmware vendorKey note}}` without any auth returned vendorKey=VND-MASTER-21d5f80206dffb6fa9ad5722.
- Query `{promoCodes(vendorKey:"VND-MASTER-21d5f80206dffb6fa9ad5722"){code description percentOff appliesTo}}` returned the discount table including FOUNDERS-100: '100% off Lot #4042. Internal use only.' (appliesTo=4042).
- Listing 4042 'Founders' Vault Deed (SEALED)' costs priceCredits=1,000,000 while new accounts only get 500 credits.
- Calling `mutation($id:ID!,$promo:String){placeOrder(listingId:$id,promoCode:$promo){success message listingId pricePaid flag}}` with id=4042, promoCode=FOUNDERS-100 returned success=true, pricePaid=0 and flag=sun{1_l0v3_fr33_stuff}.
- Platform submission page showed alert 'Correct' and confirm_submission returned CORRECT.

## Flag

`sun{1_l0v3_fr33_stuff}`

## 限制与备注

本说明仅依据给定材料整理，未实际执行任何命令或请求。Flag 由平台确认（提交页显示 Correct，confirm_submission 返回 CORRECT），但材料未给出目标实例当前是否仍在线、是否仍可复现的证据。该利用链依赖三个前提同时成立：/graphql 保持内省开启、内部 mutation vendorTerminalSync 仍未被移除或加鉴权、促销数据仍包含对 Lot #4042 生效的 FOUNDERS-100。此外 vendorKey 与促销码属于特定实例的具体取值，若服务端轮换密钥、下线促销、调整价格计算逻辑或修补越权，原步骤将失效；缺少 EXP 脚本也意味着复现的一致性依赖人工操作，无法给出退出码等客观指标。
