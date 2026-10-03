import uuid

from app.database.session import AsyncSessionFactory
from app.domains.journal_entries.repository import JournalEntryRepository
from app.domains.nlp.service import NLPService
from app.exceptions import EmptyTextError
from app.models import SentimentAnalysis


async def analyze_and_store_journal_entry_sentiment(
    journal_entry_public_id: uuid.UUID, user_id: int, text: str
) -> None:
    """Background-task entry point for analyzing and persisting journal entry sentiment.

    Creates its own database session so it can run independently of the
    request that scheduled it. Intended to be passed to FastAPI's
    BackgroundTasks. Silently returns if the journal entry no longer exists,
    the text is empty, or any other error occurs, since this runs outside
    the request/response cycle and has no caller to report failures to.

    Args:
        journal_entry_public_id: The public ID of the journal entry to
            analyze.
        user_id: The ID of the user the journal entry must belong to.
        text: The journal entry's text content to run sentiment analysis on.
    """
    try:
        async with AsyncSessionFactory() as session:
            nlp_response = await NLPService().inference(text)

            journal_entry_record = await JournalEntryRepository(
                session
            ).get_journal_entry_by_public_id_for_user(journal_entry_public_id, user_id)

            if journal_entry_record is None:
                return

            sentiment_analysis_record = SentimentAnalysis()
            sentiment_analysis_record.sentiment = nlp_response.sentiment
            sentiment_analysis_record.confidence = nlp_response.confidence
            sentiment_analysis_record.journal_entry_id = journal_entry_record.id

            session.add(sentiment_analysis_record)
            await session.commit()
    except EmptyTextError:
        return
    except Exception as exc:
        print(f"Background task error: {exc}")
