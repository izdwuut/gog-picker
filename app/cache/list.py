class List:
    @staticmethod
    def get_string_as_list(string, delimiter):
        return [elem.strip(" ") for elem in string.split(delimiter)]

    @staticmethod
    def get_not_included_keywords(string, keywords):
        normalised_string = string.lower()
        return ', '.join([keyword for keyword in keywords if keyword.lower() not in normalised_string])

    @staticmethod
    def get_tags(keywords):
        return ['[' + keyword + ']' for keyword in keywords]
