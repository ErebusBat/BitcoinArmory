# To run on OSX you have to do some funky stuff
# The export_keys script does NOT have to be part of the homebrew package
# But you have to use homebrew python packages but system python
# No idea why, but that is the way it is
# Also you probably want 
# PYTHONPATH=`brew --prefix`/lib/python2.7/site-packages /usr/bin/python export_keys.py /path/to.wallet dumpall

import sys
import getpass
import os

# Try to figure out where armory is installed
def tryAppendArmoryPath(p):
  p = os.path.abspath(p)
  if os.path.exists(os.path.join(p, 'armoryengine.py')):
    print 'Using Armory @ : ' + p
    sys.path.append(p)
    return True
  else:
    return False

foundArmory = False
if not foundArmory:
  foundArmory = tryAppendArmoryPath(os.environ.get('ARMORY_HOME',''))
if not foundArmory:
  foundArmory = tryAppendArmoryPath('..')
if not foundArmory:
  foundArmory = tryAppendArmoryPath('/usr/local/Cellar/armory-qt/0.86.3-beta/share/armory')
if not foundArmory:
  print '*** Error Can not find armory, set ARMORY_HOME'
  exit(1)

from armoryengine import *

def printAddrInfo(pubKey,privKey=None,seq=None,printHeaders=True):
  if printHeaders:
    if seq is not None:
      sys.stdout.write('seq,')
    sys.stdout.write('pubkey')
    if privKey is not None:
      sys.stdout.write(',privkey')
    print ''
  if seq is not None:
    sys.stdout.write('%04d,' % seq)
  sys.stdout.write(pubKey)
  if privKey is not None:
    sys.stdout.write(',' + privKey)
  print ''  

def unlock(): 
  if not wallet.isLocked:
    return  
  k = SecureBinaryData(getpass.getpass('decrypt passphrase:'))
  if not wallet.verifyPassphrase(k):
    print '*** ERROR: Incorrect wallet passphrase!'
    exit(1)
  wallet.unlock(securePassphrase=k)  # Will throw on error 
  
def encodePrivKeyBase58(privKeyBin):
   """
   Ported from HEAD, this function is in >=0.87, see 
   https://bitcointalk.org/index.php?topic=56424.msg1494967#msg1494967
   """
   PRIVKEYBYTE = '\x80'  # IMPORTANT: This will ONLY work for the mainnet (NOT TESTNET)
   bin33 = PRIVKEYBYTE + privKeyBin
   chk = computeChecksum(bin33)
   return binary_to_base58(bin33 + chk)

def getNewPubAddr():
  return wallet.getNextUnusedAddress().getAddrStr()
  
def getPubAddrAtIndex(i):
  return getAddrAtIndex(i).getAddrStr()
  
def getAddrAtIndex(i):
  pub_addr = wallet.getAddress160ByChainIndex(i)
  return wallet.addrMap[pub_addr]
  
def createNewPubAddrs(count=50):
  for i in range(0,count):
    pub_addr = getNewPubAddr()
    printAddrInfo(seq=i,pubKey=pub_addr,printHeaders=(i==0))
    
def dumpPubAddrs(printHeaders=True):
  for i in range(0,wallet.lastComputedChainIndex+1):
    pub_addr = getPubAddrAtIndex(i)
    printAddrInfo(seq=i, \
      pubKey=pub_addr, \
      printHeaders=(i==0 and printHeaders))
  
def dumpImportedAddrs(printHeaders=True,printSeq=False):
  unlock()
  for addrObj in wallet.addrMap.values():
    seq = addrObj.chainIndex
    if seq != -2:
      continue
    pub_key = addrObj.getAddrStr()
    priv_key = encodePrivKeyBase58(addrObj.binPrivKey32_Plain.toBinStr())    
    if not printSeq:
      seq = None
    printAddrInfo(seq=seq, \
      pubKey=pub_key, \
      privKey=priv_key, \
      printHeaders=(seq==0 and printHeaders))
  
def dumpPrivAddrs(printHeaders=True):
  unlock()
  for i in range(0,wallet.lastComputedChainIndex+1):
    addrObj = getAddrAtIndex(i)
    pub_key = addrObj.getAddrStr()
    priv_key = encodePrivKeyBase58(addrObj.binPrivKey32_Plain.toBinStr())
    printAddrInfo(seq=i, \
      pubKey=pub_key, \
      privKey=priv_key, \
      printHeaders=(i==0 and printHeaders))

#############################  START ACTUAL PROGRAM 
if len(argv)<3:
   print '\n\nUSAGE: %s <wallet file> <new #|dump|dumpPriv|dumpImport|dumpAll>' % argv[0]
   
   print '\nEXPORT: If you want to export to a file then you can feed through tail to chop'
   print 'the armory header:'
   print '  %s /path/to/full_or_watchonly.wallet new 50 | tail -n +12 > keys.txt' % argv[0]
   
   print '\nEXAMPLES:'
   print '  Generate a single new address or 50'
   print '    %s /path/to/full_or_watchonly.wallet new' % (argv[0])
   print '    %s /path/to/full_or_watchonly.wallet new 50' % (argv[0])
   print ''
   print '  Dump all previously generated public addresses in the chain'
   print '    %s /path/to/full_or_watchonly.wallet dump' % (argv[0])
   print ''
   print '  Dump all previously generated private addresses in the chain'
   print '    %s /path/to/full.wallet dumpPriv' % (argv[0])
   print ''
   print '  Dump all previously imported private addresses'
   print '    %s /path/to/full.wallet dumpImport' % (argv[0])
   print ''
   print '  Dump all private addresses private AND imported'
   print '    %s /path/to/full.wallet dumpAll' % (argv[0])
   exit(0)

# Parse args & open wallet
wallet_file = argv[1]
command = argv[2].lower()   
print '       Using wallet file : %s' % wallet_file
wallet = PyBtcWallet().readWalletFile(wallet_file)

# Run the requested command
if command == 'new':
  count = 1
  if len(argv)==4:
    count = int(argv[3])
  createNewPubAddrs(count)
elif command == 'dump':
  dumpPubAddrs()
elif command == 'dumppriv':
  dumpPrivAddrs()
elif command == 'dumpimport':
  dumpImportedAddrs()
elif command == 'dumpall':
  dumpPrivAddrs()
  dumpImportedAddrs(printHeaders=False,printSeq=True)
else:
  print '*** ERROR: I dont know how to do %s' % argv[2]
  exit(1)
