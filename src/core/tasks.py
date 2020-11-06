import logging

import requests
from background_task import background
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from mailchimp3 import MailChimp

logger = logging.getLogger(__name__)


@background(schedule=0)
def send_welcome_email(email: str) -> None:
    logger.info(f"Sending welcome email to: {email}")

    email_string = render_to_string("registration/welcome.html")
    text_string = render_to_string("registration/welcome.txt")
    try:
        response = send_mail(
            "Welcome to Operation Code!",
            text_string,
            "staff@operationcode.org",
            [email],
            html_message=email_string,
            fail_silently=False,
        )
        logger.info(f"Email to {email} response", response)

    except Exception as e:  # pragma: no cover
        logger.exception("Exception trying to send welcome email to user", e)


@background(schedule=0)
def send_slack_invite_job(email: str) -> None:
    """
    Background task that sends pybot a request triggering an invite for
    a newly registered user

    :param email: Email the user signed up with
    """
    try:
        logger.info(f"Sending slack invite for email: {email}")
        url = f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite"
        headers = {"Authorization": f"Bearer {settings.PYBOT_AUTH_TOKEN}"}
        res = requests.post(url, json={"email": email}, headers=headers)

        logger.info("Slack invite response:", res)
    except Exception as e:  # pragma: no cover
        logger.exception(
            f"Exception while trying to send slack invite for email {email}", e
        )


@background(schedule=0)
def add_user_to_mailing_list(email: str) -> None:
    """
    Adds the new user's email to our mailchimp list (which should trigger a
    welcome email)
    """
    try:
        user = AuthUser.objects.get(email=email)

        client = MailChimp(settings.MAILCHIMP_API_KEY)
        res = client.lists.members.create(
            settings.MAILCHIMP_LIST_ID,
            {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {"FNAME": user.first_name, "LNAME": user.last_name},
            },
        )

        logger.info("Added user to email list.  Response: ", res)
    except Exception as e:  # pragma: no cover
        logger.exception(f"Exception while adding email {email} to mailing list.", e)
