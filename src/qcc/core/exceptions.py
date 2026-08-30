class QCCError(Exception): pass
class ParseError(QCCError): pass
class TranslationError(QCCError): pass
class BackendError(QCCError): pass
class SessionError(QCCError): pass
