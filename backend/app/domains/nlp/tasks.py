import uuid
from typing import cast

from app.database.session import AsyncSessionFactory
from app.domains.journal_entries.repository import JournalEntryRepository
from app.domains.nlp.service import NLPService
from app.models import JournalEntry, SentimentAnalysis


async def analyze_and_store_journal_entry_sentiment(
    journal_entry_public_id: uuid.UUID, user_id: int, text: str
) -> None:
    try:
        async with AsyncSessionFactory() as session:
            nlp_response = await NLPService().inference(text)

            journal_entry_record = cast(
                JournalEntry,
                await JournalEntryRepository(
                    session
                ).get_journal_entry_by_public_id_for_user(
                    journal_entry_public_id, user_id
                ),
            )

            sentiment_analysis_record = SentimentAnalysis()
            sentiment_analysis_record.sentiment = nlp_response.sentiment
            sentiment_analysis_record.confidence = nlp_response.confidence
            sentiment_analysis_record.journal_entry_id = journal_entry_record.id

            session.add(sentiment_analysis_record)
            await session.commit()
    except Exception as exc:
        await session.rollback()
        print(f"Background task error: {exc}")
