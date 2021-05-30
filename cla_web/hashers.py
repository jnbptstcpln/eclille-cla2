from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from collections import OrderedDict


class BCryptPasswordHasher(BasePasswordHasher):
    algorithm = "bcrypt_php"
    library = ("bcrypt", "bcrypt")
    rounds = 10

    def salt(self):
        bcrypt = self._load_library()
        return bcrypt.gensalt(self.rounds)

    def encode(self, password, salt):
        bcrypt = self._load_library()
        password = password.encode()
        data = bcrypt.hashpw(password, salt)
        return f"{data.decode('ascii')}"

    def verify(self, incoming_password, encoded_db_password):
        algorithm, data = encoded_db_password.split('$', 1)
        assert algorithm == self.algorithm

        db_password_salt = data.encode('ascii')
        encoded_incoming_password = self.encode(incoming_password, db_password_salt)
        # Compare of `data` should only be done because in database we don't persist alg prefix like `bcrypt$`
        return constant_time_compare(data, encoded_incoming_password)

    def safe_summary(self, encoded):
        empty, algostr, work_factor, data = encoded.split('$', 3)
        salt, checksum = data[:22], data[22:]
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('work factor', work_factor),
            ('salt', mask_hash(salt)),
            ('checksum', mask_hash(checksum)),
        ])

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        data = encoded.split('$')
        salt = data[:29]  # Length of the salt in bcrypt.
        rounds = data.split('$')[2]
        # work factor is logarithmic, adding one doubles the load.
        diff = 2 ** (self.rounds - int(rounds)) - 1
        while diff > 0:
            self.encode(password, salt.encode('ascii'))
            diff -= 1