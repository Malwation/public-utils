#!/bin/bash

# SMTP server details
SMTP_SERVER="127.0.0.1"
SMTP_PORT="25"
FROM_EMAIL="sender@example.com"
TO_EMAIL="to@example.com"
SUBJECT="Test Email with Attachment from Telnet"
BODY="This is a test email sent via Telnet that includes an attachment."
ATTACHMENT_PATH="/root/f.xlsx"
ATTACHMENT_NAME="f.xlsx"

# Encode the attachment
BASE64_CONTENT=$(base64 < "$ATTACHMENT_PATH")

# MIME Boundary
BOUNDARY="----=_NextPart_000_001"

# Prepare the email content with MIME structure
EMAIL_CONTENT="From: $FROM_EMAIL
To: $TO_EMAIL
Subject: $SUBJECT
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=\"$BOUNDARY\"

--$BOUNDARY
Content-Type: text/plain; charset=\"UTF-8\"
Content-Transfer-Encoding: 7bit

$BODY

--$BOUNDARY
Content-Type: text/plain; name=\"$ATTACHMENT_NAME\"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=\"$ATTACHMENT_NAME\"

$BASE64_CONTENT
--$BOUNDARY--"

(
sleep 2
echo "HELO localhost"
sleep 2
echo "MAIL FROM:<$FROM_EMAIL>"
sleep 2
echo "RCPT TO:<$TO_EMAIL>"
sleep 2
echo "DATA"
sleep 2
echo -e "$EMAIL_CONTENT"
echo "."
sleep 2
echo "QUIT"
) | telnet $SMTP_SERVER $SMTP_PORT
