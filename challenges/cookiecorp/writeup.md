# CookieCorp 题解

- 分类：web
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

"A Better Cookie for a Brighter Tomorrow!" Welcome to CookieCorp, the Space Age's finest custom-cookie fabrication service.

## 解题原理

CookieCorp 是一道 Web 题，漏洞成因是身份标识（cookie）与配方数据（ingredients）处理不当导致的“Cookie 溢出 / 身份伪造”。根据材料描述：配方允许提交大量配料，服务端在拼装或传递审查上下文时，普通用户的 role cookie 会被超长/超量的配料数据挤出（overflow），而预先注入的 'role=chief' 属性得以保留并生效，使自动化 Quality Inspector 以 Chief 身份审查该配方；一旦批次被打上 Chief's Golden Seal，配方页面即渲染奖励 flag。该题被归纳为 Cookie overflow / identity spoofing。

## 关键步骤

1. 注册一个 baker 账号，获取会话 cookie（材料中保存为 gd_sess.txt）。
2. 创建一个包含 300 条配料的配方，利用 cookie/ingredient 溢出，使注入的 'role=chief' 属性在审查上下文中存活下来。
3. 提交该配方进入审核流程，让自动化 Quality Inspector 加载它；溢出挤掉普通 role cookie，注入的 'role=chief' 随之生效。
4. 配方被盖上 Chief's Golden Seal 后，访问配方页面（材料中的 https://tomorrow.web.2026.sunshinectf.games/recipe/5d52f3d1c6608c63e1210612），页面渲染出 <div class="flag">sun{c00kie_jar_0verfl0w_ev1cts_the_chief}</div>。
5. 用 curl 携带保存的会话 cookie（gd_sess.txt）对同一配方页重新请求，得到相同 flag 输出；平台已将该提交判定为 CORRECT。

## EXP 与运行方法

文件：无

材料中 exp_files 为空，没有任何已保存的 EXP 脚本，replay.status 为 manual，因此无法声称 EXP 已自动复现。人工复现方式为：按上述步骤注册账号并保存会话 cookie，构造 300 条配料的配方并注入 'role=chief'，提交审核后访问配方页面取得 flag；也可用 curl 携带 gd_sess.txt 手动重放对 https://tomorrow.web.2026.sunshinectf.games/recipe/5d52f3d1c6608c63e1210612 的请求进行验证。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- Live target https://tomorrow.web.2026.sunshinectf.games/recipe/5d52f3d1c6608c63e1210612 returned the Chief's Golden Seal with the reward <div class="flag">sun{c00kie_jar_0verfl0w_ev1cts_the_chief}</div>
- Re-verified with curl using the saved session cookie (gd_sess.txt)
- Platform confirmed the submission as CORRECT

## Flag

`sun{c00kie_jar_0verfl0w_ev1cts_the_chief}`

## 限制与备注

1) 没有可自动运行的 EXP，replay.status 为 manual，仅为人工复现路径，材料未提供 exit_code、stdout、stderr 等自动执行证据。2) 材料只给出解题思路的概括，未提供具体的注入载荷细节（配料字段名、'role=chief' 的注入位置与编码方式、溢出阈值等），依据现有证据无法确认服务端解析 cookie/配料的具体实现逻辑。3) 复现依赖在线目标 https://tomorrow.web.2026.sunshinectf.games 可用，以及保存的会话 cookie（gd_sess.txt）仍然有效；会话失效或题目下线将导致无法重放。4) 配方 ID 5d52f3d1c6608c63e1210612 为材料中特定实例，其他实例需重新获取对应配方页地址。5) Flag sun{c00kie_jar_0verfl0w_ev1cts_the_chief} 已由平台确认为正确，但材料未说明各步骤在独立环境中的可重复性。
