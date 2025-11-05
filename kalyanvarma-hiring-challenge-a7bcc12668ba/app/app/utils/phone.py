import phonenumbers

class PhoneParseError(Exception):
    pass

def normalize_phone(raw_phone, default_region='IN'):
    """Convert raw phone number to E.164 format."""
    if not raw_phone:
        raise PhoneParseError("Empty phone number.")
    try:
        if raw_phone.startswith('+'):
            pn = phonenumbers.parse(raw_phone, None)
        else:
            pn = phonenumbers.parse(raw_phone, default_region)
        if not phonenumbers.is_valid_number(pn):
            raise PhoneParseError("Invalid phone number.")
        return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        raise PhoneParseError(str(e))