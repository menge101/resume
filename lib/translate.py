from aws_xray_sdk.core import xray_recorder
from basilico import htmx
from basilico.attributes import Class, ID, Src
from basilico.elements import Div, Img, Li, Text, Ul
from lens import lens
from lib import language, return_, session
from typing import cast
import boto3
import logging
import os


logging_level = os.environ.get("logging_level", "DEBUG").upper()
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


FLAG_MAP = {
    "en": "./flags/us.svg",
    "af": "./flags/za.svg",
    "sq": "./flags/al.svg",
    "am": "./flags/et.svg",
    "ar": "./flags/arab.svg",
    "hy": "./flags/am.svg",
    "as": "./flags/az.svg",
    "bn": "./flags/bd.svg",
    "ca": "./flags/es-ct.svg",
    "zh": "./flags/cn.svg",
    "zh-tw": "./flags/cn.svg",
    "cs": "./flags/cz.svg",
    "da": "./flags/dk.svg",
    "es": "./flags/ee.svg",
    "fa": "./flags/ir.svg",
    "fa-af": "./flags/af.svg",
    "tl": "./flags/ph.svg",
    "fr-ca": "./flags/ca.svg",
    "ka": "./flags/ge.svg",
    "el": "./flags/gr.svg",
    "gu": "./flags/in.svg",
    "ha": "./flags/ng.svg",
    "he": "./flags/il.svg",
    "hi": "./flags/in.svg",
    "ga": "./flags/ie.svg",
    "ja": "./flags/jp.svg",
    "kn": "./flags/in.svg",
    "kk": "./flags/kz.svg",
    "ko": "./flags/kr.svg",
    "ms": "./flags/my.svg",
    "mr": "./flags/in.svg",
    "ps": "./flags/af.svg",
    "pt": "./flags/br.svg",
    "pt-pt": "./flags/pt.svg",
    "pa": "./flags/in.svg",
    "sr": "./flags/sx.svg",
    "si": "./flags/in.svg",
    "sl": "./flags/si.svg",
    "es-mx": "./flags/mx.svg",
    "sw": "./flags/ke.svg",
    "sv": "./flags/se.svg",
    "te": "./flags/in.svg",
    "ik": "./flags/ua.svg",
    "ir": "./flags/pk.svg",
    "vi": "./flags/vn.svg",
    "cy": "./flags/wa.svg",
}

LANGUAGE_CODE = {"FA-AF": "PRS", "PT-PT": "PT"}


@xray_recorder.capture("## Translate acting")
def act(
    data_table_name: str, session_data: session.SessionData, params: dict[str, str]
) -> tuple[session.SessionData, list[str]]:
    # This guards against the edge case where an action is requested prior to the session being initialized
    if "id_" not in session_data or "sk" not in session_data:
        raise ValueError(
            "Improperly formatted session data, likely stemming from session corruption"
        )

    # Translation element supports two actions
    # 1) Opening the choice menu
    if params.get("action") == "open":
        session_data["translate"] = {"state": "open"}
        events: list[str] = []
    # 2) Initializing the language picker
    elif params.get("action") == "init":
        session_data["translate"] = {"state": "closed"}
        events = []
    # 3) Choosing a language/localization
    else:
        supported_langs = language.get_supported(
            boto3.resource("dynamodb"), data_table_name
        )
        chosen_lang = params.get("action", "en")
        session_data["translate"] = {"state": "closed"}
        logger.debug(f"Supported languages: {supported_langs}")
        logger.debug(f"Chosen language: {chosen_lang}")
        session_data["local"] = (
            chosen_lang.lower() if chosen_lang in supported_langs else "en"
        )
        events = ["language-updated"]
    logger.debug(f"Translate act new session data: {session_data}")
    session.update_session(data_table_name, session_data)
    return session_data, events


def apply_closed_template(language: str) -> str:
    language = language.lower()
    template = Div(
        ID("language-picker"),
        Class("language no-padding no-margin"),
        htmx.Trigger("click"),
        htmx.Swap("outerHTML swap:100ms"),
        htmx.Get("/ui/translate?action=open"),
        htmx.Params("*"),
        Ul(Class("no-padding no-margin"), language_button(language)),
    )
    return template.string()


def apply_open_template(current_language: str, data_table_name: str) -> str:
    languages = language.get_supported(boto3.resource("dynamodb"), data_table_name)
    languages.sort()
    languages = [lang for lang in languages if lang != current_language]
    languages.insert(0, current_language)
    template = Div(
        ID("language-picker"),
        Class("language no-padding no-margin"),
        Ul(
            Class("no-margin no-padding"),
            *(language_button_with_htmx(lang) for lang in languages),
        ),
    )
    return template.string()


@xray_recorder.capture("## Translate building")
def build(
    table_name: str, session_data: session.SessionData, *_args, **_kwargs
) -> return_.Returnable:
    state = lens.focus(session_data, ["translate", "state"], default_result="closed")
    language = cast(str, session_data.get("local", "en"))
    if state == "open":
        template = apply_open_template(language, table_name)
    elif state == "closed":
        template = apply_closed_template(language)
    else:
        template = apply_closed_template(language)
        logger.warning(f"Unexpected state: {state}")
    return return_.http(template, status_code=200)


def get_existing_en_data(client, table_name) -> dict[str, str]:
    response = client.query(
        TableName=table_name,
        KeyConditionExpression="pk = :pkval",
        ExpressionAttributeValues={":pkval": {"S": "en"}},
    )
    return {
        lens.focus(record, ["sk", "S"]): lens.focus(record, ["text", "S"])
        for record in response.get("Items", [])
    }


def language_button(lang: str) -> Li:
    lang = lang.lower()
    flag = FLAG_MAP.get(lang, f"./flags/{lang}.svg")
    txt = LANGUAGE_CODE.get(lang, lang.upper())
    return Li(Class("lang-btn"), Text(txt), Img(Src(flag)))


def language_button_with_htmx(lang: str) -> Li:
    lang = lang.lower()
    flag = FLAG_MAP.get(lang, f"./flags/{lang}.svg")
    txt = LANGUAGE_CODE.get(lang, lang.upper())
    return Li(
        htmx.Trigger("click"),
        htmx.Swap("outerHTML swap:100ms"),
        htmx.Get("/ui/translate"),
        htmx.Vals(f'{{"action": "{lang}"}}'),
        htmx.Target("#language-picker"),
        htmx.Params("*"),
        Class("lang-btn"),
        Text(txt),
        Img(Src(flag)),
    )


# development-translation-translationdestination3f8d-dxomc4g48zcq
# arn:aws:iam::779846793683:role/development-translation-translation8773171D-1evkFF1M9IzL
# development-translation-translationsource303b34d4-rwgn7buxzupq
