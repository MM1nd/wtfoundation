from wtforms.validators import Regexp
import re

class WHATWGEmail(Regexp):
    """
    This uses the WHATWG RegEx to validate an Email.
    cf. https://html.spec.whatwg.org/multipage/forms.html#valid-e-mail-address
    So does Abide.
    cf. http://foundation.zurb.com/sites/docs/v/5.5.3/components/abide.html
    """

    def __init__(self, message = None):
        self.pattern="email"
        super().__init__(r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", re.IGNORECASE, message)

    def __call__(self, form, field):
        
        message = self.message
        
        if message is None:
            message = field.gettext('Invalid email address.')

        return super().__call__(form, field, message)