#!/usr/bin/python3
import os, sys, random, datetime, time
longrun_chance  = int(os.environ['LONGRUN_CHANCE'])
longrun_range   = os.environ['LONGRUN_RANGE']
sleep_range     = os.environ['SLEEP_RANGE']
rerun_rate      = int(os.environ['RERUN_RATE'])
fail_rate       = int(os.environ['FAIL_RATE'])
inc_start       = int(os.environ['INC_START'])
inc_duration    = int(os.environ['INC_DURATION'])
inc_percent     = float(os.environ['INC_PERCENT'])
print("=====================================")
print(f"Application:\t{os.environ['APPLIC']}")
print(f"SubApplication:\t{os.environ['APPLGROUP']}")
print(f"JobName:\t{os.environ['JOBNAME']}")
print(f"JobOID:\t\t{os.environ['ORDERID']}")
print(f"FolderOID:\t{os.environ['TABLEID']}")
print(f"RunDate:\t{os.environ['ODATE']}")
print("=====================================")
print()
rc              = 0
sleeptime       = 0
today           = datetime.datetime.now()
dom             = int(today.strftime("%d"))
print(f'Starting at {today.strftime("%Y-%m-%d %H:%M:%S")}')
print("=====================================")
print(f"SLEEP_RANGE:\t{sleep_range}")
print(f"LONGRUN_RANGE:\t{longrun_range}")
print(f"LONGRUN_CHANCE:\t{longrun_chance}")
print(f"FAIL_RATE:\t{fail_rate}")
print(f"RERUN_RATE:\t{rerun_rate}")
print("=====================================")
print()
longrun_percent = random.randint(1, 100)
if longrun_chance >= longrun_percent:
    low, high = longrun_range.split("-")
    low = int(low)
    high = int(high)
    sleeptime = random.randint(int(low), int(high))
    print("long running job")
else:
    low, high = sleep_range.split("-")
    low = int(low)
    high = int(high)
    if inc_start != 0:
        inc_end = inc_start + inc_duration
        if inc_start < dom < inc_end:
            print(f"inc_start: {inc_start}")
            print(f"dom: {dom}")
            print(f"inc_end: {inc_end}")
            inc_multiplier = dom - inc_start
            print(f"inc_multiplier: {inc_multiplier}")
            inc_amount = inc_percent * inc_multiplier
            print(f"inc_amount: {inc_amount}")
            low = low + (low * inc_amount)
            high = high + (high * inc_amount)
            print(f"new sleep_range: {low}-{high}")
    sleeptime = random.uniform(low, high)
print(f"running for {sleeptime} seconds")
fail_me = random.randint(1, 100)
print(f"fail value is {fail_me}")
rerun_me = random.randint(1, 100)
if rerun_rate >= rerun_me:
    print("rerun me please")
    print()
time.sleep(sleeptime)
if fail_rate >= fail_me:
    print("Failure")
    rc = fail_me

for name, value in os.environ.items():
    print("{0}:\t{1}".format(name, value))


sys.exit(rc)
