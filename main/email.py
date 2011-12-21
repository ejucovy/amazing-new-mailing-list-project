from django.core.mail import EmailMessage

class EmailMessageWithEnvelopeTo(EmailMessage):
    def message(self):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        msg = SafeMIMEText(smart_str(self.body, encoding),
                           self.content_subtype, encoding)
        msg = self._create_message(msg)
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = self.extra_headers.get("To", ', '.join(self.to))
        if self.cc:
            msg['Cc'] = ', '.join(self.cc)

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            msg['Message-ID'] = make_msgid()
        for name, value in self.extra_headers.items():
            if name.lower() in ('from', 'to') :  # From and To are already handled
                continue
            msg[name] = value
        return msg

        
