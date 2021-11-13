class ResponseUtilities:

    @staticmethod
    def get_inner_error_context(error_message):
        """
        function to get error context for apis
        """

        context = {
            'error_message': error_message
        }
        return context
