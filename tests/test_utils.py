""" Test utilities. """

import re

import pytest

from aries_staticagent import utils, Message
from aries_staticagent.mtc import (
    MessageTrustContext,
    AUTHCRYPT_AFFIRMED,
    AUTHCRYPT_DENIED,
    ANONCRYPT_AFFIRMED,
    ANONCRYPT_DENIED
)

REGEX = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9]) (2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'

MATCH = re.compile(REGEX).match


def test_timestamp():
    """ Test that the timestamp looks right. """
    timestamp = utils.timestamp()
    assert MATCH(timestamp)


def test_preprocess():
    """Test preprocessing decorator."""
    def preprocessor(msg):
        msg['preprocessed'] = True
        return msg

    @utils.preprocess(preprocessor)
    def test_handler(msg):
        return msg

    handled = test_handler(Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    }))
    assert handled['preprocessed']


@pytest.mark.asyncio
async def test_preprocess_async_handler():
    """Test preprocessing decorator."""
    def preprocessor(msg):
        msg['preprocessed'] = True
        return msg

    @utils.preprocess(preprocessor)
    async def test_handler(msg):
        return msg

    handled = await test_handler(Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    }))
    assert handled['preprocessed']


@pytest.mark.asyncio
async def test_preprocess_async_handler_and_preprocessor():
    """Test preprocessing decorator."""
    async def preprocessor(msg):
        msg['preprocessed'] = True
        return msg

    @utils.preprocess_async(preprocessor)
    async def test_handler(msg):
        return msg

    handled = await test_handler(Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    }))
    assert handled['preprocessed']


def test_validate():
    """Test validation of message"""
    def validator(msg):
        assert msg.id == '12345'

    @utils.validate(validator)
    def validate_test(msg):
        assert msg

    validate_test(Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    }))


def test_validate_modify_msg():
    """Test validation can modify the message."""
    def validator(msg):
        msg['modified'] = True
        return msg

    @utils.validate(validator)
    def test_handler(msg):
        assert msg['modified']

    test_handler(Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    }))


def test_validate_with_other_decorators():
    """Test validation of message"""
    def validator(msg):
        assert msg.id == '12345'
        msg['validated'] = True
        return msg

    def fake_route():
        """Register route decorator."""
        def _fake_route_decorator(func):
            return func
        return _fake_route_decorator

    @utils.validate(validator)
    @fake_route()
    def validate_test(msg):
        return msg

    @fake_route()
    @utils.validate(validator)
    def validate_test2(msg):
        return msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })

    handled = validate_test(msg)
    assert handled['validated']
    handled = validate_test2(msg)
    assert handled['validated']


def test_mtc_decorator():
    """Test the MTC decorator."""
    @utils.mtc(AUTHCRYPT_AFFIRMED, AUTHCRYPT_DENIED)
    def mtc_test(msg):
        assert msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })
    msg.mtc = MessageTrustContext(AUTHCRYPT_AFFIRMED, AUTHCRYPT_DENIED)
    mtc_test(msg)


def test_mtc_decorator_not_met():
    """Test the MTC decorator."""
    @utils.mtc(AUTHCRYPT_AFFIRMED)
    def mtc_test(msg):
        assert msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })
    msg.mtc = MessageTrustContext(AUTHCRYPT_AFFIRMED, AUTHCRYPT_DENIED)
    with pytest.raises(utils.InsufficientMessageTrust):
        mtc_test(msg)


def test_authcrypted_decorator():
    """Test the authcrypted decorator."""
    @utils.authcrypted
    def mtc_test(msg):
        assert msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })
    msg.mtc = MessageTrustContext(AUTHCRYPT_AFFIRMED, AUTHCRYPT_DENIED)
    mtc_test(msg)


def test_authcrypted_decorator_not_met():
    """Test the authcrypted decorator."""
    @utils.authcrypted
    def mtc_test(msg):
        assert msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })
    msg.mtc = MessageTrustContext(AUTHCRYPT_AFFIRMED)
    with pytest.raises(utils.InsufficientMessageTrust):
        mtc_test(msg)


def test_anoncrypted_decorator():
    """Test the anoncrypted decorator."""
    @utils.anoncrypted
    def mtc_test(msg):
        assert msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })
    msg.mtc = MessageTrustContext(ANONCRYPT_AFFIRMED, ANONCRYPT_DENIED)
    mtc_test(msg)

def test_anoncrypted_decorator_not_met():
    """Test the anoncrypted decorator."""
    @utils.anoncrypted
    def mtc_test(msg):
        assert msg

    msg = Message({
        '@type': 'doc_uri/protocol/0.1/test',
        '@id': '12345',
        'content': 'test'
    })
    msg.mtc = MessageTrustContext(ANONCRYPT_AFFIRMED)
    with pytest.raises(utils.InsufficientMessageTrust):
        mtc_test(msg)
