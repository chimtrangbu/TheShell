class Token():

    def __init__(self, string):
        self.str = string + " "
        self.len = len(self.str)
        self.i = 0
        self.tokens = ["'", '"', "`", "|", "&"]
        self.param = ''
        self.args = []
        self.key = ''

    def _is_single_quote(self):
        return self.key == "'" and self.str[self.i] != "'"

    def _is_double_quote(self):
        return self.key == '"' and (self.str[self.i] != '"' or
                                    (self._is_back_slash() and self.str[self.i] == "\""))

    def _is_back_slash(self):
        return self.str[self.i - 1] == '\\'

    def _is_back_quote(self):
        return self.key == "`" and (self.str[self.i] != "`" or
                                    (self._is_back_slash() and self.str[self.i] == "`"))

    def _is_start_param(self):
        if (self.str[self.i] in self.tokens and
                self.key not in self.tokens and self.param):
            self._add_argument()
            self._clear_param_key()
        return not self.key and self.str[self.i] != " "

    def _is_element_param(self):
        return bool(self.key) and (self._is_single_param()
                                   or self._is_element_token()
                                   or self._is_element_op())

    def _is_single_param(self):
        return self.str[self.i] != " " and self.key not in self.tokens

    def _is_element_token(self):
        return (self._is_single_quote() or
                self._is_double_quote() or
                self._is_back_quote())

    def _is_element_op(self):
        return self._is_operator_or() or self._is_operator_and()

    def _is_operator_or(self):
        return self.key == '|' and self.str[self.i] != "|"

    def _is_operator_and(self):
        return self.key == '&' and self.str[self.i] != "&"

    def _is_remove_backslash(self):
        return self.str[self.i] != '\\' or self.key in ["'", '`']

    def _add_argument(self):
        if self.key in ['`', "|", "&"]:
            self.param += self.str[self.i]
        self.args.append(self.param)

    def _add_content_param(self):
        if self._is_remove_backslash():
            self.param += self.str[self.i]

    def _clear_param_key(self):
        self.param = ''
        self.key = ''

    def _set_param_key(self):
        self.key = self.str[self.i]
        self.param = self.str[self.i] if self.key not in ['"', "'"] else ''

    def split_token(self):
        while self.i < self.len:
            # find index start param of user
            if self._is_start_param():
                self._set_param_key()

            # add element of param into variable
            elif self._is_element_param():
                self._add_content_param()

            # store param if param not empty
            elif self.param:
                self._add_argument()
                self._clear_param_key()

            self.i += 1
        return self.args
