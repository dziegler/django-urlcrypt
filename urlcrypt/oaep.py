# from https://bugs.launchpad.net/pycrypto/+bug/328027

from math import ceil
from hashlib import sha1
from Crypto.Util.strxor import strxor
from Crypto.Util.number import long_to_bytes


def make_mgf1(hash):
    """Make an MFG1 function using the given hash function.

    Given a hash function implementing the standard hash function interface,
    this function returns a Mask Generation Function using that hash.
    """
    def mgf1(mgfSeed,maskLen):
        """Mask Generation Function based on a hash function.

        Given a seed byte string 'mgfSeed', this function will generate
        and return a mask byte string  of length 'maskLen' in a manner
        approximating a Random Oracle.

        The algorithm is from PKCS#1 version 2.1, appendix B.2.1.
        """
        hLen = hash().digest_size
        if maskLen > 2**32 * hLen:
            raise ValueError("mask too long")
        T = ""
        for counter in range(int(ceil(maskLen / (hLen*1.0)))):
            C = long_to_bytes(counter)
            C = ('\x00'*(4 - len(C))) + C
            assert len(C) == 4, "counter was too big"
            T += hash(mgfSeed + C).digest()
        assert len(T) >= maskLen, "generated mask was too short"
        return T[:maskLen]
    return mgf1


MGF1_SHA1 = make_mgf1(sha1)


class OAEP(object):
    """Class implementing OAEP encoding/decoding.

    This class can be used to encode/decode byte strings using the
    Optimal Asymmetic Encryption Padding Scheme.  It requires a source
    of random bytes, a hash function and a mask generation function.
    By default SHA-1 is used as the hash function, and MGF1-SHA1 is used
    as the mask generation function.

    The method 'encode' will encode a byte string using this padding
    scheme, and the complimenary method 'decode' will decode it.

    The algorithms are from PKCS#1 version 2.1, section 7.1
    """

    def __init__(self,randbytes,hash=sha1,mgf=MGF1_SHA1):
        self.randbytes = randbytes
        self.hash = hash
        self.mgf = mgf

    def encode(self,k,M,L=""):
        """Encode a message using OAEP.

        This method encodes a byte string 'M' using Optimal Asymmetric
        Encryption Padding.  The argument 'k' must be the size of the
        private key modulus in bytes.  If specified, 'L' is a label
        for the encoding.
        """
        # Calculate label hash, unless it is too long
        if L:
            limit = getattr(self.hash,"input_limit",None)
            if limit and len(L) > limit:
                raise ValueError("label too long")
        lHash = self.hash(L).digest()
        # Check length of message against size of key modulus
        mLen = len(M)
        hLen = len(lHash)
        if mLen > k - 2*hLen - 2:
            raise ValueError("message too long")
        # Perform the encoding
        PS = "\x00" * (k - mLen - 2*hLen - 2)
        DB = lHash + PS + "\x01" + M
        assert len(DB) == k - hLen - 1, "DB length is incorrect"
        seed = self.randbytes(hLen)
        dbMask = self.mgf(seed,k - hLen - 1)
        maskedDB = strxor(DB,dbMask)
        seedMask = self.mgf(maskedDB,hLen)
        maskedSeed = strxor(seed,seedMask)
        return "\x00" + maskedSeed + maskedDB

    def decode(self,k,EM,L=""):
        """Decode a message using OAEP.

        This method decodes a byte string 'EM' using Optimal Asymmetric
        Encryption Padding.  The argument 'k' must be the size of the
        private key modulus in bytes.  If specified, 'L' is the label
        used for the encoding.
        """
        # Generate label hash, for sanity checking
        lHash = self.hash(L).digest()
        hLen = len(lHash)
        # Split the encoded message
        Y = EM[0]
        maskedSeed = EM[1:hLen+1]
        maskedDB = EM[hLen+1:]
        # Perform the decoding
        seedMask = self.mgf(maskedDB,hLen)
        seed = strxor(maskedSeed,seedMask)
        dbMask = self.mgf(seed,k - hLen - 1)
        DB = strxor(maskedDB,dbMask)
        # Split the DB string
        lHash1 = DB[:hLen]
        x01pos = hLen
        while x01pos < len(DB) and DB[x01pos] != "\x01":
            x01pos += 1
        PS = DB[hLen:x01pos]
        M = DB[x01pos+1:]
        # All sanity-checking done at end, to avoid timing attacks
        valid = True
        if x01pos == len(DB):  # No \x01 byte
            valid = False
        if lHash1 != lHash:    # Mismatched label hash
            valid = False
        if Y != "\x00":        # Invalid leading byte
            valid = False
        if not valid:
            raise ValueError("decryption error")
        return M


def test_oaep():
    """Run through the OAEP encode/decode for lots of random values."""
    from os import urandom
    p = OAEP(urandom)
    for k in xrange(45,300):
        for i in xrange(0,1000):
            b = i % (k - 2*20 - 3)  # message length
            if b == 0:
                j = -1
            else:
                j = i % b           # byte to corrupt
            print "test %s:%s (%s bytes, corrupt at %s)" % (k,i,b,j)
            msg = urandom(b)
            pmsg = p.encode(k,msg)
            #  Test that padding actually does something
            assert msg != pmsg, "padded message was just the message"
            #  Test that padding is removed correctly
            assert p.decode(k,pmsg) == msg, "message was not decoded properly"
            #  Test that corrupted padding gives an error
            try:
                if b == 0: raise ValueError
                newb = urandom(1)
                while newb == pmsg[j]:
                    newb = urandom(1)
                pmsg2 = pmsg[:j] + newb + pmsg[j+1:]
                p.decode(k,pmsg2)
            except ValueError:
                pass
            else:
                raise AssertionError("corrupted padding was still decoded")

