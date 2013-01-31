# cd /usr/local/Cellar/armory-qt/0.86.3-beta/share/armory 
# PYTHONPATH=`brew --prefix`/lib/python2.7/site-packages /usr/bin/python export_keys.py

import sys
import getpass
sys.path.append('/usr/local/Cellar/armory-qt/0.86.3-beta/share/armory') # change to whereever armory is

from armoryengine import *
wallet = PyBtcWallet().readWalletFile('/Users/aburns/Library/Application Support/Armory/armory_37KiZPH1q_.wallet')

def getNewPubAddr():
  return wallet.getNextUnusedAddress().getAddrStr()
  
def getPubAddrAtIndex(i):
  if i > wallet.lastComputedChainIndex:
    print "*** END OF CHAIN ***"
    return ""
  pub_addr = wallet.getAddress160ByChainIndex(i)
  return wallet.addrMap[pub_addr].getAddrStr()

def dumpPubAddrs():
  for i in range(0,250):
    # pub_addr = getNewPubAddr()
    pub_addr = getPubAddrAtIndex(i)
    if pub_addr == "":
      exit()
    print "%03d: %s" % (i,pub_addr)
    
def dumpPrivAddrs():
  k = SecureBinaryData(getpass.getpass('decrypt passphrase:'))
  wallet.unlock(securePassphrase=k)  # Will throw on error
  print '"idx","pubkey","privkey"'
  for addrObj in wallet.addrMap.values():
    pub_key = addrObj.getAddrStr()
    # priv_key = encodePrivKeyBase58(addrObj.binPrivKey32_Plain.toBinStr())
    priv_key = ""
    print "\"%s\",\"%s\",\"%s\"" % (addrObj.chainIndex,pub_key, priv_key)
   
# dumpPubAddrs()
dumpPrivAddrs()
