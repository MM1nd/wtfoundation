from wtforms.widgets import HTMLString
from wtforms.validators import Length
from warnings import warn

try:
    from html import escape
except ImportError:
    from cgi import escape


from wtforms.compat import text_type, iteritems


def html_params(**kwargs):
    """
    This is Verbatim from WTForms BUT ``aria_`` is handled like ``data_``

    Generate HTML attribute syntax from inputted keyword arguments.
    The output value is sorted by the passed keys, to provide consistent output
    each time this function is called with the same parameters. Because of the
    frequent use of the normally reserved keywords `class` and `for`, suffixing
    these with an underscore will allow them to be used.
    In order to facilitate the use of ``data-`` attributes, the first underscore
    behind the ``data``-element is replaced with a hyphen.
    >>> html_params(data_any_attribute='something')
    'data-any_attribute="something"'
    In addition, the values ``True`` and ``False`` are special:
      * ``attr=True`` generates the HTML compact output of a boolean attribute,
        e.g. ``checked=True`` will generate simply ``checked``
      * ``attr=False`` will be ignored and generate no output.
    >>> html_params(name='text1', id='f', class_='text')
    'class="text" id="f" name="text1"'
    >>> html_params(checked=True, readonly=False, name="text1", abc="hello")
    'abc="hello" checked name="text1"'
    """
    params = []
    for k, v in sorted(iteritems(kwargs)):
        if k in ('class_', 'class__', 'for_'):
            k = k[:-1]
        elif k.startswith('data_') or k.startswith('aria_') :
            k = k.replace('_', '-', 1)
        if v is True:
            params.append(k)
        elif v is False:
            pass
        else:
            params.append('%s="%s"' % (text_type(k), escape(text_type(v), quote=True)))
    return ' '.join(params)



class RowInput(object):
    """
    Replaces WTForms.Input AND WTForms.PasswordInput

    Render a basic ``<input>`` field.

    BUT Take up the entire row AND render the label AND translate validators into abide/html5

    This is used as the basis for most of the other input fields.
    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """

    html_params = staticmethod(html_params)

    custom_patterns = {}

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs and self.input_type!="password":
            kwargs['value'] = field._value()
        if self.input_type=="password":
            kwargs['value'] = ""

        
        pattern = None
        length_validator = None

        for validator in field.validators:
            try:
                new_pattern = validator.pattern
                assert (not pattern), "Do not mix validators that define a pattern"
                pattern = new_pattern
            except AttributeError:
                pass

            if isinstance(validator,Length):
                assert (not length_validator), "Do no use multiple Length validators"
                length_validator = validator
                if validator.min!=-1:
                    kwargs["minlength"]=validator.min
                if validator.max!=-1:
                    kwargs["maxlength"]=validator.max

        if length_validator and length_validator.min!=-1 and pattern:
            warn("Field %s has a minimum length requirement that will not be enforced on client side by contemporary browsers." % field.id)

        if length_validator and not pattern:
            pattern = field.id
            custom_pattern = r"/^(.){%d,%s}$/" % (0 if length_validator.min == -1 else length_validator.min, "" if length_validator.max == -1 else "%d")
            if length_validator.max!=-1:
                custom_pattern = custom_pattern % length_validator.max
            
            if field.id in RowInput.custom_patterns and RowInput.custom_patterns[field.id]!=custom_pattern:
                warn("Field %s validation pattern has been overridden. This might indicate that the field.id is not unique application wide." & field.id)
            RowInput.custom_patterns[field.id]=custom_pattern
        if pattern:
            kwargs["pattern"]=pattern


        desc_id = field.id+"-desc"

        div_row = "<div %s>\n%s\n%s\n</div>" % (self.html_params(class_="row"), "%s", "%s")
        
        div_label_col = "<div %s>\n%s\n</div>" % (self.html_params(class_="large-2 columns show-for-large"), "%s")
        div_label_col_label = "<label %s>%s</label>" % (self.html_params(class_="text-right middle", for_=field.id), field.label)
        div_label_col = div_label_col % div_label_col_label

        div_col = "<div %s>\n%s\n%s\n%s\n</div>"  % (self.html_params(class_="small-12 large-10 columns"), "%s", "%s", "%s")
        label = "<label %s>%s</label>" % (self.html_params(class_="hide-for-large", for_=field.id), field.label)

        input = "<input %s %s>" % (self.html_params(name=field.name, aria_describedby=desc_id, **kwargs), "required" if field.flags.required else "")
        desc = "<p %s>%s</p>" % (self.html_params(class_="help-text", id=desc_id), field.description)

        div_col = div_col % (label, input, desc)
        div_row = div_row % (div_label_col, div_col)

        return HTMLString(div_row)