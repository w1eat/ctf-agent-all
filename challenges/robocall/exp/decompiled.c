
/* ===== _init @ 00101000 ===== */

int _init(EVP_PKEY_CTX *ctx)

{
  undefined *puVar1;
  
  puVar1 = PTR___gmon_start___00107508;
  if (PTR___gmon_start___00107508 != (undefined *)0x0) {
    puVar1 = (undefined *)(*(code *)PTR___gmon_start___00107508)();
  }
  return (int)puVar1;
}


/* ===== FUN_00101020 @ 00101020 ===== */

void FUN_00101020(void)

{
  (*(code *)PTR_001074b8)();
  return;
}


/* ===== __cxa_finalize @ 001010a0 ===== */

void __cxa_finalize(void)

{
  (*(code *)PTR___cxa_finalize_00107518)();
  return;
}


/* ===== _exit @ 001010b0 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _exit(int __status)

{
  (*(code *)PTR__exit_001074c0)();
  return;
}


/* ===== write @ 001010c0 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t write(int __fd,void *__buf,size_t __n)

{
  ssize_t sVar1;
  
  sVar1 = (*(code *)PTR_write_001074c8)();
  return sVar1;
}


/* ===== nanosleep @ 001010d0 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int nanosleep(timespec *__requested_time,timespec *__remaining)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_nanosleep_001074d0)();
  return iVar1;
}


/* ===== close @ 001010e0 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int close(int __fd)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_close_001074d8)();
  return iVar1;
}


/* ===== read @ 001010f0 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t read(int __fd,void *__buf,size_t __nbytes)

{
  ssize_t sVar1;
  
  sVar1 = (*(code *)PTR_read_001074e0)();
  return sVar1;
}


/* ===== setvbuf @ 00101100 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int setvbuf(FILE *__stream,char *__buf,int __modes,size_t __n)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_setvbuf_001074e8)();
  return iVar1;
}


/* ===== open @ 00101110 ===== */

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int open(char *__file,int __oflag,...)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_open_001074f0)();
  return iVar1;
}


/* ===== _start @ 00101120 ===== */

void processEntry _start(undefined8 param_1,undefined8 param_2)

{
  undefined1 auStack_8 [8];
  
  (*(code *)PTR___libc_start_main_001074f8)(main,param_2,&stack0x00000008,0,0,param_1,auStack_8);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}


/* ===== deregister_tm_clones @ 00101150 ===== */

/* WARNING: Removing unreachable block (ram,0x00101163) */
/* WARNING: Removing unreachable block (ram,0x0010116f) */

void deregister_tm_clones(void)

{
  return;
}


/* ===== register_tm_clones @ 00101180 ===== */

/* WARNING: Removing unreachable block (ram,0x001011a4) */
/* WARNING: Removing unreachable block (ram,0x001011b0) */

void register_tm_clones(void)

{
  return;
}


/* ===== __do_global_dtors_aux @ 001011c0 ===== */

void __do_global_dtors_aux(void)

{
  if (completed_0 == '\0') {
    if (PTR___cxa_finalize_00107518 != (undefined *)0x0) {
      __cxa_finalize(__dso_handle);
    }
    deregister_tm_clones();
    completed_0 = 1;
    return;
  }
  return;
}


/* ===== frame_dummy @ 00101200 ===== */

void frame_dummy(void)

{
  register_tm_clones();
  return;
}


/* ===== raw_print @ 00101209 ===== */

void raw_print(void *param_1)

{
  undefined8 local_10;
  
  for (local_10 = 0; *(char *)((long)param_1 + local_10) != '\0'; local_10 = local_10 + 1) {
  }
  if (local_10 != 0) {
    write(1,param_1,local_10);
  }
  return;
}


/* ===== raw_eprint @ 00101259 ===== */

void raw_eprint(void *param_1)

{
  undefined8 local_10;
  
  for (local_10 = 0; *(char *)((long)param_1 + local_10) != '\0'; local_10 = local_10 + 1) {
  }
  if (local_10 != 0) {
    write(2,param_1,local_10);
  }
  return;
}


/* ===== raw_print_int @ 001012a9 ===== */

void raw_print_int(uint param_1)

{
  uint uVar1;
  long lVar2;
  char local_48 [32];
  char acStack_28 [20];
  uint local_14;
  uint local_10;
  int local_c;
  
  local_c = 0;
  if (-1 < (int)param_1) {
    local_14 = param_1;
  }
  else {
    local_48[0] = '-';
    local_14 = -param_1;
  }
  local_10 = (uint)(-1 >= (int)param_1);
  if (local_14 == 0) {
    local_c = 1;
    acStack_28[0] = '0';
  }
  for (; local_14 != 0; local_14 = local_14 / 10) {
    lVar2 = (long)local_c;
    local_c = local_c + 1;
    acStack_28[lVar2] = (char)local_14 + (char)(local_14 / 10) * -10 + '0';
  }
  while (uVar1 = local_10, local_c != 0) {
    local_c = local_c + -1;
    local_10 = local_10 + 1;
    local_48[(int)uVar1] = acStack_28[local_c];
  }
  write(1,local_48,(long)(int)local_10);
  return;
}


/* ===== raw_readline @ 0010139c ===== */

long raw_readline(long param_1,int param_2)

{
  char local_19;
  ssize_t local_18;
  int local_c;
  
  local_c = 0;
  do {
    if (param_2 + -1 <= local_c) {
LAB_0010141b:
      *(undefined1 *)(param_1 + local_c) = 0;
      return param_1;
    }
    local_18 = read(0,&local_19,1);
    if (local_18 < 1) {
      if (local_c == 0) {
                    /* WARNING: Subroutine does not return */
        _exit(0);
      }
      goto LAB_0010141b;
    }
    if (local_19 == '\n') goto LAB_0010141b;
    *(char *)(local_c + param_1) = local_19;
    local_c = local_c + 1;
  } while( true );
}


/* ===== raw_parse_int @ 00101431 ===== */

undefined8 raw_parse_int(long param_1,int *param_2)

{
  int iVar1;
  undefined8 uVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  for (local_c = 0; (*(char *)(param_1 + local_c) == ' ' || (*(char *)(param_1 + local_c) == '\t'));
      local_c = local_c + 1) {
  }
  local_10 = 1;
  if (*(char *)(param_1 + local_c) == '-') {
    local_10 = -1;
    local_c = local_c + 1;
  }
  else if (*(char *)(param_1 + local_c) == '+') {
    local_c = local_c + 1;
  }
  if ((*(char *)(param_1 + local_c) < '0') || ('9' < *(char *)(param_1 + local_c))) {
    uVar2 = 0;
  }
  else {
    iVar1 = 0;
    for (; ('/' < *(char *)(param_1 + local_c) && (*(char *)(param_1 + local_c) < ':'));
        local_c = local_c + 1) {
      iVar1 = *(char *)(param_1 + local_c) + -0x30 + iVar1 * 10;
    }
    *param_2 = local_10 * iVar1;
    uVar2 = 1;
  }
  return uVar2;
}


/* ===== get_random_number @ 0010156c ===== */

undefined8 get_random_number(void)

{
  undefined8 local_18;
  int local_c;
  
  local_c = open("/dev/urandom",0);
  if (local_c < 0) {
    raw_eprint("Failed to open /dev/urandom. (challenge not functioning as intended)\n");
    local_18 = 1;
  }
  else {
    local_18 = 0;
    read(local_c,&local_18,8);
    close(local_c);
  }
  return local_18;
}


/* ===== get_a_fun_fact @ 001015de ===== */

undefined8 get_a_fun_fact(void)

{
  ulong uVar1;
  timespec local_a8;
  timespec local_98;
  timespec local_88;
  timespec local_78;
  timespec local_68;
  timespec local_58;
  timespec local_48;
  timespec local_38;
  timespec local_28;
  timespec local_18;
  
  uVar1 = get_random_number();
  switch(uVar1 % 0xb) {
  default:
    scream(0xb);
    raw_print(&DAT_00104658);
    break;
  case 1:
    raw_print(
             "Premium Cable Inc has commited millions of dollars to providing disadvantaged communities and at-need children across the solar system with the internet they need to pursue an education in partnership with the OLPC program.\n"
             );
    local_18.tv_sec = (__time_t)be_annoying;
    local_18.tv_nsec = 0;
    nanosleep(&local_18,(timespec *)0x0);
    break;
  case 2:
    raw_print("We here at Premium Cable Inc make a commitment to putting the customer first!\n");
    local_28.tv_sec = (__time_t)be_annoying;
    local_28.tv_nsec = 0;
    nanosleep(&local_28,(timespec *)0x0);
    break;
  case 3:
    raw_print(
             "Premium Cable Inc used to be a part of CableCast, we hope to continue their customer service excellence.\n"
             );
    local_38.tv_sec = (__time_t)be_annoying;
    local_38.tv_nsec = 0;
    nanosleep(&local_38,(timespec *)0x0);
    break;
  case 4:
    raw_print(
             "Did you know that Premium Cable Inc is reported by independent outlets to be the most reliable data service in the solar system?\n"
             );
    local_48.tv_sec = (__time_t)be_annoying;
    local_48.tv_nsec = 0;
    nanosleep(&local_48,(timespec *)0x0);
    break;
  case 5:
    raw_print(
             "Premium Cable Inc is a people first company, we have commited to giving a share of our sales to blind awareness communities.\n"
             );
    local_58.tv_sec = (__time_t)be_annoying;
    local_58.tv_nsec = 0;
    nanosleep(&local_58,(timespec *)0x0);
    break;
  case 6:
    raw_print(
             "Premium Cable Inc is an equal opportunity employer. Working with us helps empower those in need and give them a place to work.\n"
             );
    local_68.tv_sec = (__time_t)be_annoying;
    local_68.tv_nsec = 0;
    nanosleep(&local_68,(timespec *)0x0);
    break;
  case 7:
    raw_print(
             "By shopping with Premium Cable Inc you are helping us plant forests to save Earth, Thank you for your contributions!\n"
             );
    local_78.tv_sec = (__time_t)be_annoying;
    local_78.tv_nsec = 0;
    nanosleep(&local_78,(timespec *)0x0);
    break;
  case 8:
    raw_print(
             "By shopping with Premium Cable Inc you are helping us fund our efforts to be carbon negative, Thanks for your contributions!\n"
             );
    local_88.tv_sec = (__time_t)be_annoying;
    local_88.tv_nsec = 0;
    nanosleep(&local_88,(timespec *)0x0);
    break;
  case 9:
    raw_print(
             "We here at Premium Cable Inc commit a portion of our profits to help fund Sweetums Cares, a non-profit group that puts umbrella hats on homeless people when it rains."
             );
    local_98.tv_sec = (__time_t)be_annoying;
    local_98.tv_nsec = 0;
    nanosleep(&local_98,(timespec *)0x0);
    break;
  case 10:
    raw_print(
             "By shopping with Premium Cable Inc you are contributing to our reFREEEZE fund! Thank you for helping cool Earth! With this fund we plan to reFREEZE the melted ice at the equator and ship it back to the artic\n"
             );
    local_a8.tv_sec = (__time_t)be_annoying;
    local_a8.tv_nsec = 0;
    nanosleep(&local_a8,(timespec *)0x0);
  }
  return 0;
}


/* ===== place_flag @ 001018ac ===== */

undefined8 place_flag(void)

{
  int iVar1;
  ssize_t sVar2;
  undefined1 local_2068 [64];
  undefined1 local_2028 [8208];
  int local_18;
  int local_14;
  int local_10;
  int local_c;
  
  for (local_c = 0; local_c < 0x2000; local_c = local_c + 1) {
    local_2028[local_c] = 0;
  }
  local_18 = open("flag.txt",0);
  if (local_18 < 0) {
    raw_eprint(&DAT_001046d0);
                    /* WARNING: Subroutine does not return */
    _exit(1);
  }
  sVar2 = read(local_18,local_2068,0x3c);
  local_14 = (int)sVar2;
  close(local_18);
  if (local_14 < 0) {
    local_14 = 0;
  }
  for (local_c = 0; (local_c < 0xd && (local_c * 4 < local_14)); local_c = local_c + 1) {
    iVar1 = *(int *)(CHUNK_DEPTH + (long)local_c * 4);
    for (local_10 = 0; (local_10 < 4 && (local_10 + local_c * 4 < local_14));
        local_10 = local_10 + 1) {
      local_2028[(long)local_10 + (long)(0x19dc - iVar1)] = local_2068[local_c * 4 + local_10];
    }
  }
  return 0;
}


/* ===== main @ 00101a0d ===== */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 main(void)

{
  int local_10c;
  undefined1 local_108 [256];
  
  local_10c = 0;
  place_flag();
  userData = 1;
  _DAT_00107584 = 0;
  raw_print(&DAT_00104710);
  raw_print("Press enter to start.");
  raw_readline(local_108,0x100);
  raw_parse_int(local_108,&local_10c);
  if (local_10c == 0x2a) {
    be_annoying = 0;
  }
  start_position();
  return 0;
}


/* ===== start_position @ 00101aab ===== */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 start_position(void)

{
  long lVar1;
  undefined8 uVar2;
  int local_10c;
  undefined1 local_108 [256];
  
  local_10c = 0;
  _DAT_00107584 = 0;
  raw_print("1. Call Premium Cable Inc.\n");
  raw_print("2. Email Premium Cable Inc.\n");
  raw_print("3. Scream in a mix of frustration and hatred towards the FTC.\n");
  while ((3 < local_10c || (local_10c < 1))) {
    lVar1 = raw_readline(local_108,0x100);
    if (lVar1 == 0) {
      raw_print(&DAT_00104818);
    }
    raw_parse_int(local_108,&local_10c);
    if ((3 < local_10c) || (local_10c < 1)) {
      raw_print("That is an invalid input, please enter a number 1 through 3.\n");
    }
  }
  if (local_10c == 3) {
    raw_print("On a scale of 1 to 10 how frustrated are you?\n");
    raw_readline(local_108,0x100);
    raw_parse_int(local_108,&local_10c);
    scream(local_10c % 0xb);
    start_position();
  }
  else if (local_10c < 4) {
    if (local_10c == 1) {
      uVar2 = initial_call();
      return uVar2;
    }
    if (local_10c == 2) {
      uVar2 = initial_email();
      return uVar2;
    }
  }
  return 0;
}


/* ===== initial_call @ 00101c29 ===== */

undefined8 initial_call(void)

{
  undefined8 uVar1;
  timespec local_178;
  timespec local_168;
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  int local_10c;
  undefined1 local_108 [256];
  
  local_10c = 0;
  prompt("Ring ring ring...\n",0,0);
  prompt("Thanks for calling Premium Cable Inc!\n",0,0);
  prompt("This call is being recored for quaility assurance and training purposes.\n",0,0);
  while ((6 < local_10c || (local_10c < 1))) {
    raw_print("If you are looking to start a plan with us, please press 1.\n");
    local_128.tv_sec = (__time_t)be_annoying;
    local_128.tv_nsec = 0;
    nanosleep(&local_128,(timespec *)0x0);
    raw_print("If you are looking to report a service outage, please press 2.\n");
    local_138.tv_sec = (__time_t)be_annoying;
    local_138.tv_nsec = 0;
    nanosleep(&local_138,(timespec *)0x0);
    raw_print("For the billing department, please press 3.\n");
    local_148.tv_sec = (__time_t)be_annoying;
    local_148.tv_nsec = 0;
    nanosleep(&local_148,(timespec *)0x0);
    raw_print("For techincal support, please press 4.\n");
    local_158.tv_sec = (__time_t)be_annoying;
    local_158.tv_nsec = 0;
    nanosleep(&local_158,(timespec *)0x0);
    raw_print("To upgrade or change your service, please press 5.\n");
    local_168.tv_sec = (__time_t)be_annoying;
    local_168.tv_nsec = 0;
    nanosleep(&local_168,(timespec *)0x0);
    raw_print("For all other inquiries or to speak to a representitive, please press 6.\n");
    local_178.tv_sec = (__time_t)be_annoying;
    local_178.tv_nsec = 0;
    nanosleep(&local_178,(timespec *)0x0);
    raw_print("To hear these options again, please press 7.\n");
    prompt(0,local_108,0x100);
    raw_parse_int(local_108,&local_10c);
    if ((7 < local_10c) || (local_10c < 1)) {
      raw_print("That is an invalid input, please enter a number 1 through 7.\n");
    }
  }
  switch(local_10c) {
  case 1:
    uVar1 = start_service();
    break;
  case 2:
    uVar1 = report_outage();
    break;
  case 3:
    uVar1 = billing_department();
    break;
  case 4:
    uVar1 = technical_support();
    break;
  case 5:
    uVar1 = upgrade_or_change();
    break;
  case 6:
    uVar1 = other_inquiries();
    break;
  default:
    uVar1 = 0;
  }
  return uVar1;
}


/* ===== start_service @ 00101ee1 ===== */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 start_service(void)

{
  long lVar1;
  timespec local_1c8;
  timespec local_1b8;
  timespec local_1a8;
  timespec local_198;
  timespec local_188;
  timespec local_178;
  timespec local_168;
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  int local_10c;
  undefined1 local_108 [256];
  
  raw_print("We are happy to help you start a plan with us!\n");
  local_128.tv_sec = (__time_t)be_annoying;
  local_128.tv_nsec = 0;
  nanosleep(&local_128,(timespec *)0x0);
  get_a_fun_fact();
  prompt("Please enter the address you would like service to see the plans we can offer you!",
         local_108,0x100);
  local_138.tv_sec = (__time_t)be_annoying;
  local_138.tv_nsec = 0;
  nanosleep(&local_138,(timespec *)0x0);
  raw_print("Looks like we have three great offers for your location.\n");
  local_148.tv_sec = (__time_t)be_annoying;
  local_148.tv_nsec = 0;
  nanosleep(&local_148,(timespec *)0x0);
  raw_print("Press 1 to select our premium cable only plan for $73.88 a month.\n");
  local_158.tv_sec = (__time_t)be_annoying;
  local_158.tv_nsec = 0;
  nanosleep(&local_158,(timespec *)0x0);
  raw_print("Press 2 to select our premium interplanet internet plan for $122.78 a month.\n");
  local_168.tv_sec = (__time_t)be_annoying;
  local_168.tv_nsec = 0;
  nanosleep(&local_168,(timespec *)0x0);
  raw_print(
           "Press 3 to select the bundled premium cable and interplanet internet for a discounted $198.98 a month.\n"
           );
  lVar1 = raw_readline(local_108,0x100);
  if (lVar1 == 0) {
    raw_print(&DAT_00104818);
  }
  raw_parse_int(local_108,&local_10c);
  local_178.tv_sec = (__time_t)be_annoying;
  local_178.tv_nsec = 0;
  nanosleep(&local_178,(timespec *)0x0);
  if (local_10c == 1) {
    raw_print("You\'ve selected the basic cable plan.\n");
    local_1a8.tv_sec = (__time_t)be_annoying;
    local_1a8.tv_nsec = 0;
    nanosleep(&local_1a8,(timespec *)0x0);
    userData = 1;
  }
  else if (local_10c == 2) {
    raw_print("You\'ve selected the basic interplanet internet plan.\n");
    local_1b8.tv_sec = (__time_t)be_annoying;
    local_1b8.tv_nsec = 0;
    nanosleep(&local_1b8,(timespec *)0x0);
    userData = 2;
  }
  else {
    raw_print("You\'ve selected the bundled cable and interplanet internet plan.\n");
    local_1c8.tv_sec = (__time_t)be_annoying;
    local_1c8.tv_nsec = 0;
    nanosleep(&local_1c8,(timespec *)0x0);
    userData = 3;
  }
  prompt("In a momment you will be asked for your account information so we can set up your account\n"
         ,0,0);
  prompt("Please enter the phone number you want associated with your account.\n",local_108,0x100);
  prompt("Please enter the address you want service at.\n",local_108,0x100);
  prompt("Please enter the name of your first pet.\n",local_108,0x100);
  prompt("Account creation sucessful!\n",0,0);
  _DAT_00107584 = 1;
  raw_print("In a momment you will be asked for your payment information so we can set billing\n");
  local_188.tv_sec = (__time_t)be_annoying;
  local_188.tv_nsec = 0;
  nanosleep(&local_188,(timespec *)0x0);
  payment_info();
  raw_print("Plan purchase complete, thanks for shopping with us!\n");
  local_198.tv_sec = (__time_t)be_annoying;
  local_198.tv_nsec = 0;
  nanosleep(&local_198,(timespec *)0x0);
  raw_print(&DAT_00104f70);
  return 0;
}


/* ===== report_outage @ 001022d0 ===== */

void report_outage(void)

{
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  timespec local_118;
  undefined1 local_108 [256];
  
  raw_print("Thanks for helping us work towards a ZERO outage network!\n");
  local_118.tv_sec = (__time_t)be_annoying;
  local_118.tv_nsec = 0;
  nanosleep(&local_118,(timespec *)0x0);
  raw_print("Please report the outage address:\n");
  local_128.tv_sec = (__time_t)be_annoying;
  local_128.tv_nsec = 0;
  nanosleep(&local_128,(timespec *)0x0);
  raw_readline(local_108,0x100);
  local_138.tv_sec = (__time_t)be_annoying;
  local_138.tv_nsec = 0;
  nanosleep(&local_138,(timespec *)0x0);
  raw_print("Thanks for reporting the outage!\n");
  local_148.tv_sec = (__time_t)be_annoying;
  local_148.tv_nsec = 0;
  nanosleep(&local_148,(timespec *)0x0);
  raw_print("Goodbye!\n");
  local_158.tv_sec = (__time_t)be_annoying;
  local_158.tv_nsec = 0;
  nanosleep(&local_158,(timespec *)0x0);
  start_position();
  return;
}


/* ===== billing_department @ 0010241c ===== */

void billing_department(void)

{
  long lVar1;
  timespec local_188;
  timespec local_178;
  timespec local_168;
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  int local_10c;
  undefined1 local_108 [256];
  
  raw_print("You\'ve reached the billing department\n");
  local_128.tv_sec = (__time_t)be_annoying;
  local_128.tv_nsec = 0;
  nanosleep(&local_128,(timespec *)0x0);
  login_roleplay();
  raw_print("If you are here to pay an unpaid bill press 1.\n");
  local_138.tv_sec = (__time_t)be_annoying;
  local_138.tv_nsec = 0;
  nanosleep(&local_138,(timespec *)0x0);
  raw_print("If you would like to update which card you are billed from press 2.\n");
  local_148.tv_sec = (__time_t)be_annoying;
  local_148.tv_nsec = 0;
  nanosleep(&local_148,(timespec *)0x0);
  lVar1 = raw_readline(local_108,0x100);
  if (lVar1 == 0) {
    raw_print(&DAT_00104818);
  }
  raw_parse_int(local_108,&local_10c);
  local_158.tv_sec = (__time_t)be_annoying;
  local_158.tv_nsec = 0;
  nanosleep(&local_158,(timespec *)0x0);
  if (local_10c == 1) {
    raw_print(
             "In a moment you will be asked for your payment information, by continuing you agree to the autopay terms and conditions that can be found on our website.\n"
             );
    local_178.tv_sec = (__time_t)be_annoying;
    local_178.tv_nsec = 0;
    nanosleep(&local_178,(timespec *)0x0);
  }
  else {
    if (local_10c != 2) {
      billing_department();
      return;
    }
    raw_print("Enter the updated card information:\n");
    local_188.tv_sec = (__time_t)be_annoying;
    local_188.tv_nsec = 0;
    nanosleep(&local_188,(timespec *)0x0);
  }
  payment_info();
  raw_print("Payment information submitted\n");
  local_168.tv_sec = (__time_t)be_annoying;
  local_168.tv_nsec = 0;
  nanosleep(&local_168,(timespec *)0x0);
  start_position();
  return;
}


/* ===== technical_support @ 00102636 ===== */

void technical_support(void)

{
  long lVar1;
  timespec local_168;
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  int local_10c;
  undefined1 local_108 [256];
  
  raw_print("Thanks for calling techincal support!\n");
  local_128.tv_sec = (__time_t)be_annoying;
  local_128.tv_nsec = 0;
  nanosleep(&local_128,(timespec *)0x0);
  raw_print("If you would like to report an outage please press 1.\n");
  local_138.tv_sec = (__time_t)be_annoying;
  local_138.tv_nsec = 0;
  nanosleep(&local_138,(timespec *)0x0);
  raw_print("If you need equipment replaced press 2.\n");
  local_148.tv_sec = (__time_t)be_annoying;
  local_148.tv_nsec = 0;
  nanosleep(&local_148,(timespec *)0x0);
  lVar1 = raw_readline(local_108,0x100);
  if (lVar1 == 0) {
    raw_print(&DAT_00104818);
  }
  raw_parse_int(local_108,&local_10c);
  local_158.tv_sec = (__time_t)be_annoying;
  local_158.tv_nsec = 0;
  nanosleep(&local_158,(timespec *)0x0);
  if (local_10c == 1) {
    report_outage();
  }
  else {
    if (local_10c != 2) {
      technical_support();
      return;
    }
    login_roleplay();
    raw_print("New equipment will be send to the address we have on file at cost of $54.96\n");
    local_168.tv_sec = (__time_t)be_annoying;
    local_168.tv_nsec = 0;
    nanosleep(&local_168,(timespec *)0x0);
  }
  start_position();
  return;
}


/* ===== upgrade_or_change @ 001027d6 ===== */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void upgrade_or_change(void)

{
  long lVar1;
  timespec local_188;
  timespec local_178;
  timespec local_168;
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  int local_10c;
  undefined1 local_108 [256];
  
  get_a_fun_fact();
  raw_print("We are always happy to help you upgrade your plan!\n");
  local_128.tv_sec = (__time_t)be_annoying;
  local_128.tv_nsec = 0;
  nanosleep(&local_128,(timespec *)0x0);
  raw_print(
           "If you would like to upgrade to the bundled premium cable and INTERplaNET internet for a discounted $198.98 a month, press 1.\n"
           );
  local_138.tv_sec = (__time_t)be_annoying;
  local_138.tv_nsec = 0;
  nanosleep(&local_138,(timespec *)0x0);
  raw_print(
           "To modify your plan to one of the other plan options you will need to recreate your customer account by pressing 2.\n"
           );
  local_148.tv_sec = (__time_t)be_annoying;
  local_148.tv_nsec = 0;
  nanosleep(&local_148,(timespec *)0x0);
  lVar1 = raw_readline(local_108,0x100);
  if (lVar1 == 0) {
    raw_print(&DAT_00104818);
  }
  raw_parse_int(local_108,&local_10c);
  local_158.tv_sec = (__time_t)be_annoying;
  local_158.tv_nsec = 0;
  nanosleep(&local_158,(timespec *)0x0);
  if (_DAT_00107584 == 0) {
    login_roleplay();
  }
  if (local_10c == 1) {
    if (userData == 3) {
      raw_print("You already have the best plan! That\'s great news!\n");
      local_178.tv_sec = (__time_t)be_annoying;
      local_178.tv_nsec = 0;
      nanosleep(&local_178,(timespec *)0x0);
    }
    else {
      raw_print("You\'re plan has been upgraded, thanks for working with us! Have a great day!!!\n")
      ;
      local_168.tv_sec = (__time_t)be_annoying;
      local_168.tv_nsec = 0;
      nanosleep(&local_168,(timespec *)0x0);
      userData = 3;
      start_position();
    }
    start_position();
  }
  else if (local_10c == 2) {
    raw_print(
             "Your old account will be deleted as soon as the first payment from the new account is received.\n"
             );
    local_188.tv_sec = (__time_t)be_annoying;
    local_188.tv_nsec = 0;
    nanosleep(&local_188,(timespec *)0x0);
    start_service();
  }
  else {
    upgrade_or_change();
  }
  return;
}


/* ===== other_inquiries @ 00102a25 ===== */

void other_inquiries(void)

{
  long lVar1;
  timespec local_198;
  timespec local_188;
  timespec local_178;
  timespec local_168;
  timespec local_158;
  timespec local_148;
  timespec local_138;
  timespec local_128;
  int local_10c;
  undefined1 local_108 [256];
  
  get_a_fun_fact();
  raw_print("Here at Premium Cable Inc we do our best to answer all of your questions.\n");
  local_128.tv_sec = (__time_t)be_annoying;
  local_128.tv_nsec = 0;
  nanosleep(&local_128,(timespec *)0x0);
  raw_print("If you would like to refer a friend press 1.\n");
  local_138.tv_sec = (__time_t)be_annoying;
  local_138.tv_nsec = 0;
  nanosleep(&local_138,(timespec *)0x0);
  raw_print("To cancel your plan with us press 2.\n");
  local_148.tv_sec = (__time_t)be_annoying;
  local_148.tv_nsec = 0;
  nanosleep(&local_148,(timespec *)0x0);
  raw_print("To speak with an operator press 3.\n");
  local_158.tv_sec = (__time_t)be_annoying;
  local_158.tv_nsec = 0;
  nanosleep(&local_158,(timespec *)0x0);
  lVar1 = raw_readline(local_108,0x100);
  if (lVar1 == 0) {
    raw_print(&DAT_00104818);
  }
  raw_parse_int(local_108,&local_10c);
  local_168.tv_sec = (__time_t)be_annoying;
  local_168.tv_nsec = 0;
  nanosleep(&local_168,(timespec *)0x0);
  if (local_10c == 3) {
    speak_with_an_operator();
    return;
  }
  if (local_10c < 4) {
    if (local_10c == 1) {
      raw_print(
               "Please enter the phone number of the friend you would like to refer and we will reach out to them. Referrals give you $5 off of your next payment.\n"
               );
      local_178.tv_sec = (__time_t)be_annoying;
      local_178.tv_nsec = 0;
      nanosleep(&local_178,(timespec *)0x0);
      lVar1 = raw_readline(local_108,0x100);
      if (lVar1 == 0) {
        raw_print(&DAT_00104818);
      }
      local_188.tv_sec = (__time_t)be_annoying;
      local_188.tv_nsec = 0;
      nanosleep(&local_188,(timespec *)0x0);
      raw_print("Thanks for making a referral!\n");
      local_198.tv_sec = (__time_t)be_annoying;
      local_198.tv_nsec = 0;
      nanosleep(&local_198,(timespec *)0x0);
      return;
    }
    if (local_10c == 2) {
      cancel_plan();
      return;
    }
  }
  speak_with_an_operator();
  return;
}


/* ===== cancel_plan @ 00102cb0 ===== */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void cancel_plan(void)

{
  long lVar1;
  timespec local_438;
  timespec local_428;
  timespec local_418;
  timespec local_408;
  timespec local_3f8;
  timespec local_3e8;
  timespec local_3d8;
  timespec local_3c8;
  timespec local_3b8;
  timespec local_3a8;
  timespec local_398;
  timespec local_388;
  timespec local_378;
  timespec local_368;
  timespec local_358;
  timespec local_348;
  timespec local_338;
  timespec local_328;
  timespec local_318;
  timespec local_308;
  timespec local_2f8;
  timespec local_2e8;
  timespec local_2d8;
  timespec local_2c8;
  timespec local_2b8;
  timespec local_2a8;
  timespec local_298;
  timespec local_288;
  timespec local_278;
  timespec local_268;
  timespec local_258;
  timespec local_248;
  timespec local_238;
  timespec local_228;
  int local_20c;
  undefined1 local_208 [512];
  
  if (_DAT_00107584 == 0) {
    login_roleplay();
  }
  get_a_fun_fact();
  raw_print("With this said, are you sure you want to stop working with us?\n");
  local_228.tv_sec = (__time_t)be_annoying;
  local_228.tv_nsec = 0;
  nanosleep(&local_228,(timespec *)0x0);
  raw_print("Press 1 for no.\n");
  local_238.tv_sec = (__time_t)be_annoying;
  local_238.tv_nsec = 0;
  nanosleep(&local_238,(timespec *)0x0);
  raw_print("Press 8 for yes.\n");
  local_248.tv_sec = (__time_t)be_annoying;
  local_248.tv_nsec = 0;
  nanosleep(&local_248,(timespec *)0x0);
  lVar1 = raw_readline(local_208,0x200);
  if (lVar1 == 0) {
    raw_print(&DAT_00104818);
  }
  raw_parse_int(local_208,&local_20c);
  local_258.tv_sec = (__time_t)be_annoying;
  local_258.tv_nsec = 0;
  nanosleep(&local_258,(timespec *)0x0);
  if (local_20c == 1) {
    start_position();
  }
  else {
    raw_print("Are you not sure?\n");
    local_268.tv_sec = (__time_t)be_annoying;
    local_268.tv_nsec = 0;
    nanosleep(&local_268,(timespec *)0x0);
    raw_print("Press 1 for no.\n");
    local_278.tv_sec = (__time_t)be_annoying;
    local_278.tv_nsec = 0;
    nanosleep(&local_278,(timespec *)0x0);
    raw_print("Press 8 for yes.\n");
    local_288.tv_sec = (__time_t)be_annoying;
    local_288.tv_nsec = 0;
    nanosleep(&local_288,(timespec *)0x0);
    lVar1 = raw_readline(local_208,0x200);
    if (lVar1 == 0) {
      raw_print(&DAT_00104818);
    }
    raw_parse_int(local_208,&local_20c);
    local_298.tv_sec = (__time_t)be_annoying;
    local_298.tv_nsec = 0;
    nanosleep(&local_298,(timespec *)0x0);
    raw_print("You\'ve entered \"");
    raw_print_int(local_20c);
    raw_print("\", are you sure?\n");
    if (local_20c == 1) {
      raw_print("Please tell us why you don\'t want to continue your service:\n");
      local_2a8.tv_sec = (__time_t)be_annoying;
      local_2a8.tv_nsec = 0;
      nanosleep(&local_2a8,(timespec *)0x0);
      raw_print("Press 1 if your service isn\'t meeting your standards.\n");
      local_2b8.tv_sec = (__time_t)be_annoying;
      local_2b8.tv_nsec = 0;
      nanosleep(&local_2b8,(timespec *)0x0);
      raw_print("Press 2 if you have an outage.\n");
      local_2c8.tv_sec = (__time_t)be_annoying;
      local_2c8.tv_nsec = 0;
      nanosleep(&local_2c8,(timespec *)0x0);
      raw_print("Press 3 if you have technical issues.\n");
      local_2d8.tv_sec = (__time_t)be_annoying;
      local_2d8.tv_nsec = 0;
      nanosleep(&local_2d8,(timespec *)0x0);
      raw_print("Press 4 if the price is outside of your budget.\n");
      local_2e8.tv_sec = (__time_t)be_annoying;
      local_2e8.tv_nsec = 0;
      nanosleep(&local_2e8,(timespec *)0x0);
      raw_print("Press 5 to enter your own reason.\n");
      local_2f8.tv_sec = (__time_t)be_annoying;
      local_2f8.tv_nsec = 0;
      nanosleep(&local_2f8,(timespec *)0x0);
      lVar1 = raw_readline(local_208,0x200);
      if (lVar1 == 0) {
        raw_print(&DAT_00104818);
      }
      raw_parse_int(local_208,&local_20c);
      local_308.tv_sec = (__time_t)be_annoying;
      local_308.tv_nsec = 0;
      nanosleep(&local_308,(timespec *)0x0);
      switch(local_20c) {
      default:
        start_position();
        return;
      case 1:
        upgrade_or_change();
        break;
      case 2:
        report_outage();
        break;
      case 3:
        technical_support();
        break;
      case 4:
        get_a_fun_fact();
        cancel_plan();
        break;
      case 5:
        raw_print(
                 "Please tell us why you don\'t want to work with the best cable and internet service in the the solar system.\n"
                 );
        local_318.tv_sec = (__time_t)be_annoying;
        local_318.tv_nsec = 0;
        nanosleep(&local_318,(timespec *)0x0);
        lVar1 = raw_readline(local_208,0x200);
        if (lVar1 == 0) {
          raw_print(&DAT_00104818);
        }
        local_328.tv_sec = (__time_t)be_annoying;
        local_328.tv_nsec = 0;
        nanosleep(&local_328,(timespec *)0x0);
        get_a_fun_fact();
        raw_print("With this said, are you sure you want to stop working with us?\n");
        local_338.tv_sec = (__time_t)be_annoying;
        local_338.tv_nsec = 0;
        nanosleep(&local_338,(timespec *)0x0);
        raw_print("Press 8 for no.\n");
        local_348.tv_sec = (__time_t)be_annoying;
        local_348.tv_nsec = 0;
        nanosleep(&local_348,(timespec *)0x0);
        raw_print("Press 3 for yes.\n");
        local_358.tv_sec = (__time_t)be_annoying;
        local_358.tv_nsec = 0;
        nanosleep(&local_358,(timespec *)0x0);
        lVar1 = raw_readline(local_208,0x200);
        if (lVar1 == 0) {
          raw_print(&DAT_00104818);
        }
        raw_parse_int(local_208,&local_20c);
        local_368.tv_sec = (__time_t)be_annoying;
        local_368.tv_nsec = 0;
        nanosleep(&local_368,(timespec *)0x0);
        if (local_20c != 3) {
          start_position();
          return;
        }
        raw_print(
                 "We just want to know why you don\'t want to work with the number one data service in the solar system.\n"
                 );
        local_378.tv_sec = (__time_t)be_annoying;
        local_378.tv_nsec = 0;
        nanosleep(&local_378,(timespec *)0x0);
        lVar1 = raw_readline(local_208,0x200);
        if (lVar1 == 0) {
          raw_print(&DAT_00104818);
        }
        local_388.tv_sec = (__time_t)be_annoying;
        local_388.tv_nsec = 0;
        nanosleep(&local_388,(timespec *)0x0);
        get_a_fun_fact();
        raw_print("With this said, are you sure you want to stop working with us?\n");
        local_398.tv_sec = (__time_t)be_annoying;
        local_398.tv_nsec = 0;
        nanosleep(&local_398,(timespec *)0x0);
        raw_print("Press 3 for no.\n");
        local_3a8.tv_sec = (__time_t)be_annoying;
        local_3a8.tv_nsec = 0;
        nanosleep(&local_3a8,(timespec *)0x0);
        raw_print("Press 0 for yes.\n");
        local_3b8.tv_sec = (__time_t)be_annoying;
        local_3b8.tv_nsec = 0;
        nanosleep(&local_3b8,(timespec *)0x0);
        lVar1 = raw_readline(local_208,0x200);
        if (lVar1 == 0) {
          raw_print(&DAT_00104818);
        }
        raw_parse_int(local_208,&local_20c);
        local_3c8.tv_sec = (__time_t)be_annoying;
        local_3c8.tv_nsec = 0;
        nanosleep(&local_3c8,(timespec *)0x0);
        if (local_20c != 0) {
          start_position();
          return;
        }
        raw_print(
                 "Please tell us why you don\'t want to work with the most environmentally conscious data service in the the solar system.\n"
                 );
        local_3d8.tv_sec = (__time_t)be_annoying;
        local_3d8.tv_nsec = 0;
        nanosleep(&local_3d8,(timespec *)0x0);
        lVar1 = raw_readline(local_208,0x200);
        if (lVar1 == 0) {
          raw_print(&DAT_00104818);
        }
        local_3e8.tv_sec = (__time_t)be_annoying;
        local_3e8.tv_nsec = 0;
        nanosleep(&local_3e8,(timespec *)0x0);
        get_a_fun_fact();
        raw_print("With this said, are you unsure you want to stop working with us?\n");
        local_3f8.tv_sec = (__time_t)be_annoying;
        local_3f8.tv_nsec = 0;
        nanosleep(&local_3f8,(timespec *)0x0);
        raw_print("Press 0 for no.\n");
        local_408.tv_sec = (__time_t)be_annoying;
        local_408.tv_nsec = 0;
        nanosleep(&local_408,(timespec *)0x0);
        raw_print("Press 5 for yes.\n");
        local_418.tv_sec = (__time_t)be_annoying;
        local_418.tv_nsec = 0;
        nanosleep(&local_418,(timespec *)0x0);
        lVar1 = raw_readline(local_208,0x200);
        if (lVar1 == 0) {
          raw_print(&DAT_00104818);
        }
        raw_parse_int(local_208,&local_20c);
        local_428.tv_sec = (__time_t)be_annoying;
        local_428.tv_nsec = 0;
        nanosleep(&local_428,(timespec *)0x0);
        if (local_20c != 0) {
          start_position();
          return;
        }
        raw_print(
                 "Understood, we are sad to be parting ways with you and to no longer have you a part of our green initiative, transferring you to an operator for canceling your plan...\n"
                 );
        local_438.tv_sec = (__time_t)be_annoying;
        local_438.tv_nsec = 0;
        nanosleep(&local_438,(timespec *)0x0);
        speak_with_an_operator();
      }
      start_position();
    }
    else {
      start_position();
    }
  }
  return;
}


/* ===== speak_with_an_operator @ 00103776 ===== */

void speak_with_an_operator(void)

{
  uint uVar1;
  ulong uVar2;
  timespec local_78;
  timespec local_68;
  timespec local_58;
  timespec local_48;
  timespec local_38;
  timespec local_28;
  timespec local_18;
  
  raw_print("Transferring you to speak with one of our trusted operators...\n");
  local_18.tv_sec = (__time_t)be_annoying;
  local_18.tv_nsec = 0;
  nanosleep(&local_18,(timespec *)0x0);
  raw_print("Ring ring ring!\n");
  local_28.tv_sec = (__time_t)be_annoying;
  local_28.tv_nsec = 0;
  nanosleep(&local_28,(timespec *)0x0);
  raw_print("Ring ring ring!\n");
  local_38.tv_sec = (__time_t)be_annoying;
  local_38.tv_nsec = 0;
  nanosleep(&local_38,(timespec *)0x0);
  raw_print("Ring ring ring!\n");
  local_48.tv_sec = (__time_t)be_annoying;
  local_48.tv_nsec = 0;
  nanosleep(&local_48,(timespec *)0x0);
  raw_print("Ring ring ring!\n");
  local_58.tv_sec = (__time_t)be_annoying;
  local_58.tv_nsec = 0;
  nanosleep(&local_58,(timespec *)0x0);
  raw_print(
           "It appears all of our Cable Ambassadors are busy helping other customers at this moment, please hold.\n"
           );
  local_68.tv_sec = (__time_t)be_annoying;
  local_68.tv_nsec = 0;
  nanosleep(&local_68,(timespec *)0x0);
  do {
    raw_print("***hold music***\n");
    local_78.tv_sec = (__time_t)(be_annoying * 3);
    local_78.tv_nsec = 0;
    nanosleep(&local_78,(timespec *)0x0);
    uVar1 = get_random_number();
    if ((uVar1 & 3) == 0) {
      get_a_fun_fact();
    }
    uVar2 = get_random_number();
  } while (uVar2 % 100 != 0);
  raw_print("Call dropped\n");
  start_position();
  return;
}


/* ===== payment_info @ 00103964 ===== */

undefined8 payment_info(void)

{
  undefined1 local_108 [256];
  
  prompt("Please enter your credit card number.",local_108,0x100);
  prompt("Please enter your cards security code.",local_108,0x100);
  prompt("Please enter the name on the card.",local_108,0x100);
  prompt("Please enter the expiration date on your card.",local_108,0x100);
  return 0;
}


/* ===== login_roleplay @ 001039f2 ===== */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 login_roleplay(void)

{
  undefined1 local_108 [256];
  
  prompt("In a momment you will be asked for your account information so we can look up your account\n"
         ,0,0);
  prompt("Please enter the phone number associated with your account.",local_108,0x100);
  prompt("Please enter the address we have on file.",local_108,0x100);
  prompt("Please enter the name of your first pet.",local_108,0x100);
  prompt("Login Sucessful!\n",0,0);
  _DAT_00107584 = 1;
  return 0;
}


/* ===== initial_email @ 00103a9e ===== */

undefined8 initial_email(void)

{
  prompt("You wait to hear back about that email\n",0,0);
  return 0;
}


/* ===== scream @ 00103ac6 ===== */

undefined8 scream(int param_1)

{
  int local_c;
  
  for (local_c = param_1; local_c != 0; local_c = local_c + -1) {
    raw_print(&DAT_00105db8);
  }
  raw_print(&DAT_00105dbd);
  raw_print("In Space No One Can Hear You Scream\n");
  raw_print(&DAT_00105dbd);
  return 0;
}


/* ===== prompt @ 00103b24 ===== */

undefined8 prompt(long param_1,long param_2,undefined4 param_3)

{
  long lVar1;
  timespec local_18;
  
  if (param_1 != 0) {
    raw_print(param_1);
    raw_print(&DAT_00105dbd);
  }
  if (param_2 != 0) {
    lVar1 = raw_readline(param_2,param_3);
    if (lVar1 == 0) {
      raw_print(&DAT_00104818);
    }
  }
  local_18.tv_sec = (__time_t)be_annoying;
  local_18.tv_nsec = 0;
  nanosleep(&local_18,(timespec *)0x0);
  return 0;
}


/* ===== pwnable_unbuffer_init @ 00103bb5 ===== */

void pwnable_unbuffer_init(void)

{
  setvbuf(stdout,(char *)0x0,2,0);
  setvbuf(stderr,(char *)0x0,2,0);
  return;
}


/* ===== _fini @ 00103bfc ===== */

void _fini(void)

{
  return;
}


/* ===== __libc_start_main @ 00108000 ===== */

/* WARNING: Control flow encountered bad instruction data */

void __libc_start_main(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* __libc_start_main@GLIBC_2.34 */
  halt_baddata();
}


/* ===== _ITM_deregisterTMCloneTable @ 00108008 ===== */

/* WARNING: Control flow encountered bad instruction data */

void _ITM_deregisterTMCloneTable(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* ===== _exit @ 00108010 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _exit(int __status)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* _exit@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== write @ 00108018 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t write(int __fd,void *__buf,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* write@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== nanosleep @ 00108020 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int nanosleep(timespec *__requested_time,timespec *__remaining)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* nanosleep@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== close @ 00108028 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int close(int __fd)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* close@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== read @ 00108030 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t read(int __fd,void *__buf,size_t __nbytes)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* read@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== __gmon_start__ @ 00108038 ===== */

/* WARNING: Control flow encountered bad instruction data */

void __gmon_start__(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* ===== setvbuf @ 00108040 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int setvbuf(FILE *__stream,char *__buf,int __modes,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* setvbuf@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== open @ 00108048 ===== */

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int open(char *__file,int __oflag,...)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* open@GLIBC_2.2.5 */
  halt_baddata();
}


/* ===== _ITM_registerTMCloneTable @ 00108050 ===== */

/* WARNING: Control flow encountered bad instruction data */

void _ITM_registerTMCloneTable(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}


/* ===== __cxa_finalize @ 00108058 ===== */

/* WARNING: Control flow encountered bad instruction data */

void __cxa_finalize(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
                    /* __cxa_finalize@GLIBC_2.2.5 */
  halt_baddata();
}

