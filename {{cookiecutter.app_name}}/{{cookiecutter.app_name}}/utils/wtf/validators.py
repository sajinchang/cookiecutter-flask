import datetime as dt
import ipaddress
import math
import re
import typing as T
import uuid

try:
    import email_validator
except ImportError:
    email_validator = None  # type: ignore

from .errors import StopValidation, ValidationError


class Length:
    """
    Validates the length of a string.

    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.

    When supported, sets the `minlength` and `maxlength` attributes on widgets.
    """

    def __init__(self, min=-1, max=-1, message=None):
        assert (
            min != -1 or max != -1
        ), "At least one of `min` or `max` must be specified."
        assert max == -1 or min <= max, "`min` cannot be more than `max`."
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, value):
        length = value and len(value) or 0
        if length >= self.min and (self.max == -1 or length <= self.max):
            return

        if self.message is not None:
            message = self.message

        elif self.max == -1:
            message = "Field must be at least %(min)d characters long." % {
                "min": self.min
            }

        elif self.min == -1:
            message = "Field cannot be longer than %(max)d characters." % {
                "max": self.max
            }

        elif self.min == self.max:
            message = "Field must be exactly %(max)d characters long." % {
                "max": self.max
            }

        else:
            message = "Field must be between %(min)d and %(max)d characters long." % {
                "max": self.max,
                "min": self.min,
            }

        raise ValidationError(message % dict(min=self.min, max=self.max, length=length))


class NumberRange:
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.

    When supported, sets the `min` and `max` attributes on widgets.
    """

    def __init__(self, min=None, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, value):
        if (
            value is not None
            and not math.isnan(value)
            and (self.min is None or value >= self.min)
            and (self.max is None or value <= self.max)
        ):
            return

        if self.message is not None:
            message = self.message

        # we use %(min)s interpolation to support floats, None, and
        # Decimals without throwing a formatting exception.
        elif self.max is None:
            message = "Number must be at least %(min)s." % {"min": self.min}

        elif self.min is None:
            message = "Number must be at most %(max)s." % {"max": self.max}

        else:
            message = "Number must be between %(min)s and %(max)s." % {
                "max": self.max,
                "min": self.min,
            }

        raise ValidationError(message % dict(min=self.min, max=self.max))


class DataRequired:
    """
    Checks the field's data is 'truthy' otherwise stops the validation chain.

    This validator checks that the ``data`` attribute on the field is a 'true'
    value (effectively, it does ``if field.data``.) Furthermore, if the data
    is a string type, a string containing only whitespace characters is
    considered false.

    If the data is empty, also removes prior errors (such as processing errors)
    from the field.

    **NOTE** this validator used to be called `Required` but the way it behaved
    (requiring coerced data, not input data) meant it functioned in a way
    which was not symmetric to the `Optional` validator and furthermore caused
    confusion with certain fields which coerced data to 'falsey' values like
    ``0``, ``Decimal(0)``, ``time(0)`` etc. Unless a very specific reason
    exists, we recommend using the :class:`InputRequired` instead.

    :param message:
        Error message to raise in case of a validation error.

    Sets the `required` attribute on widgets.
    """

    def __init__(self, message=None):
        self.message = message
        self.field_flags = {"required": True}

    def __call__(self, value):
        if value and (not isinstance(value, str) or value.strip()):
            return

        if self.message is None:
            message = "This field is required."
        else:
            message = self.message

        # field.errors[:] = []
        raise StopValidation(message)


class Regexp:
    """
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, value, message=None):
        match = self.regex.match(value or "")
        if match:
            return match

        if message is None:
            if self.message is None:
                message = "Invalid input."
            else:
                message = self.message

        raise ValidationError(message)


class Email:
    """
    Validates an email address. Requires email_validator package to be
    installed. For ex: pip install wtforms[email].

    :param message:
        Error message to raise in case of a validation error.
    :param granular_message:
        Use validation failed message from email_validator library
        (Default False).
    :param check_deliverability:
        Perform domain name resolution check (Default False).
    :param allow_smtputf8:
        Fail validation for addresses that would require SMTPUTF8
        (Default True).
    :param allow_empty_local:
        Allow an empty local part (i.e. @example.com), e.g. for validating
        Postfix aliases (Default False).
    """

    def __init__(
        self,
        message=None,
        granular_message=False,
        check_deliverability=False,
        allow_smtputf8=True,
        allow_empty_local=False,
    ):
        if email_validator is None:  # pragma: no cover
            raise Exception("Install 'email_validator' for email validation support.")
        self.message = message
        self.granular_message = granular_message
        self.check_deliverability = check_deliverability
        self.allow_smtputf8 = allow_smtputf8
        self.allow_empty_local = allow_empty_local

    def __call__(self, value):
        try:
            if value is None:
                raise email_validator.EmailNotValidError()
            email_validator.validate_email(
                value,
                check_deliverability=self.check_deliverability,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
            )
        except email_validator.EmailNotValidError as e:
            message = self.message
            if message is None:
                if self.granular_message:
                    message = str(e)
                else:
                    message = "Invalid email address."
            raise ValidationError(message) from e


class IPAddress:
    """
    Validates an IP address.

    :param ipv4:
        If True, accept IPv4 addresses as valid (default True)
    :param ipv6:
        If True, accept IPv6 addresses as valid (default False)
    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, ipv4=True, ipv6=False, message=None):
        if not ipv4 and not ipv6:
            raise ValueError(
                "IP Address Validator must have at least one of ipv4 or ipv6 enabled."
            )
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.message = message

    def __call__(self, value):
        # value = field.data
        valid = False
        if value:
            valid = (self.ipv4 and self.check_ipv4(value)) or (
                self.ipv6 and self.check_ipv6(value)
            )

        if valid:
            return

        message = self.message
        if message is None:
            message = "Invalid IP address."
        raise ValidationError(message)

    @classmethod
    def check_ipv4(cls, value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if not isinstance(address, ipaddress.IPv4Address):
            return False

        return True

    @classmethod
    def check_ipv6(cls, value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if not isinstance(address, ipaddress.IPv6Address):
            return False

        return True


class MacAddress(Regexp):
    """
    Validates a MAC address.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None):
        pattern = r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"
        super().__init__(pattern, message=message)

    def __call__(self, value):
        message = self.message
        if message is None:
            message = "Invalid Mac address."

        super().__call__(value, message)


class URL(Regexp):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, require_tld=True, message=None):
        regex = (
            r"^[a-z]+://"
            r"(?P<host>[^\/\?:]+)"
            r"(?P<port>:[0-9]+)?"
            r"(?P<path>\/.*?)?"
            r"(?P<query>\?.*)?$"
        )
        super().__init__(regex, re.IGNORECASE, message)
        self.validate_hostname = HostnameValidation(
            require_tld=require_tld, allow_ip=True
        )

    def __call__(self, value):
        message = self.message
        if message is None:
            message = "Invalid URL."

        match = super().__call__(value, message)
        if not self.validate_hostname(match.group("host")):
            raise ValidationError(message)


class UUID:
    """
    Validates a UUID.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, value):
        message = self.message
        if message is None:
            message = "Invalid UUID."
        try:
            uuid.UUID(value)
        except ValueError as exc:
            raise ValidationError(message) from exc


class AnyOf:
    """
    Compares the incoming data to a sequence of valid inputs.

    :param values:
        A sequence of valid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """

    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = self.default_values_formatter
        self.values_formatter = values_formatter

    def __call__(self, value):
        if value in self.values:
            return

        message = self.message
        if message is None:
            message = "Invalid value, must be one of: %(values)s."

        raise ValidationError(message % dict(values=self.values_formatter(self.values)))

    @staticmethod
    def default_values_formatter(values):
        return ", ".join(str(x) for x in values)


class NoneOf:
    """
    Compares the incoming data to a sequence of invalid inputs.

    :param values:
        A sequence of invalid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """

    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = self.default_values_formatter
        self.values_formatter = values_formatter

    def __call__(self, value):
        if value not in self.values:
            return

        message = self.message
        if message is None:
            message = "Invalid value, can't be any of: %(values)s."

        raise ValidationError(message % dict(values=self.values_formatter(self.values)))

    @staticmethod
    def default_values_formatter(v):
        return ", ".join(str(x) for x in v)


class HostnameValidation:
    """
    Helper class for checking hostnames for validation.

    This is not a validator in and of itself, and as such is not exported.
    """

    hostname_part = re.compile(r"^(xn-|[a-z0-9_]+)(-[a-z0-9_-]+)*$", re.IGNORECASE)
    tld_part = re.compile(r"^([a-z]{2,20}|xn--([a-z0-9]+-)*[a-z0-9]+)$", re.IGNORECASE)

    def __init__(self, require_tld=True, allow_ip=False):
        self.require_tld = require_tld
        self.allow_ip = allow_ip

    def __call__(self, hostname):
        if self.allow_ip and (
            IPAddress.check_ipv4(hostname) or IPAddress.check_ipv6(hostname)
        ):
            return True

        # Encode out IDNA hostnames. This makes further validation easier.
        try:
            hostname = hostname.encode("idna")
        except UnicodeError:
            pass

        # Turn back into a string in Python 3x
        if not isinstance(hostname, str):
            hostname = hostname.decode("ascii")

        if len(hostname) > 253:
            return False

        # Check that all labels in the hostname are valid
        parts = hostname.split(".")
        for part in parts:
            if not part or len(part) > 63:
                return False
            if not self.hostname_part.match(part):
                return False

        if self.require_tld and (len(parts) < 2 or not self.tld_part.match(parts[-1])):
            return False

        return True


class DateTime:
    """
    Validates a UUID.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None, format="%Y-%m-%d %H:%M:%S"):
        self.message = message
        self.format = format

    def __call__(self, value):
        message = self.message
        if message is None:
            message = "Invalid datetime."
        try:
            if isinstance(value, str):
                dt.datetime.strptime(value, self.format)
        except Exception:
            raise ValidationError(message)


class ChoiceFiled:
    def __init__(self, message=None, choice_list: T.Union[T.Iterable, None] = None):
        self.message = message
        self.choice_list = choice_list

    def __call__(self, value):
        message = self.message
        if message is None:
            message = "Invalid choice."
        if value not in self.choice_list:
            raise ValidationError(message)


email = Email
ip_address = IPAddress
mac_address = MacAddress
length = Length
number_range = NumberRange
data_required = DataRequired
regexp = Regexp
url = URL
any_of = AnyOf
none_of = NoneOf
datetime = DateTime
