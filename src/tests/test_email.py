from django.core import mail


def test_email_sanity(mailoutbox):
    """
    Do a sanity check to ensure that the testing setup for emails works.
    """
    email = mail.EmailMessage(
        subject="Sanity check",
        body="Hi there, nobody!",
        from_email="from@example.com",
        to=["to1@example.com"],
    )
    email.send()

    assert len(mailoutbox) == 1
