"""Initial schema.

Revision ID: 20260316_0001
Revises:
Create Date: 2026-03-16
"""

from alembic import op
import sqlalchemy as sa


revision = "20260316_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("posted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_job_postings_id", "job_postings", ["id"])
    op.create_index("ix_job_postings_source", "job_postings", ["source"])
    op.create_index("ix_job_postings_external_id", "job_postings", ["external_id"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_posting_id", sa.Integer(), sa.ForeignKey("job_postings.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(), nullable=True),
        sa.Column("last_response_at", sa.DateTime(), nullable=True),
        sa.Column("next_follow_up_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_applications_id", "applications", ["id"])
    op.create_index("ix_applications_job_posting_id", "applications", ["job_posting_id"])
    op.create_index("ix_applications_status", "applications", ["status"])

    op.create_table(
        "interviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("stage", sa.String(length=100), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_interviews_id", "interviews", ["id"])
    op.create_index("ix_interviews_application_id", "interviews", ["application_id"])

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("kind", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_documents_id", "documents", ["id"])
    op.create_index("ix_documents_application_id", "documents", ["application_id"])
    op.create_index("ix_documents_kind", "documents", ["kind"])

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_contacts_id", "contacts", ["id"])
    op.create_index("ix_contacts_application_id", "contacts", ["application_id"])

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_activity_logs_id", "activity_logs", ["id"])
    op.create_index("ix_activity_logs_application_id", "activity_logs", ["application_id"])
    op.create_index("ix_activity_logs_event_type", "activity_logs", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_activity_logs_event_type", table_name="activity_logs")
    op.drop_index("ix_activity_logs_application_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_id", table_name="activity_logs")
    op.drop_table("activity_logs")
    op.drop_index("ix_contacts_application_id", table_name="contacts")
    op.drop_index("ix_contacts_id", table_name="contacts")
    op.drop_table("contacts")
    op.drop_index("ix_documents_kind", table_name="documents")
    op.drop_index("ix_documents_application_id", table_name="documents")
    op.drop_index("ix_documents_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_interviews_application_id", table_name="interviews")
    op.drop_index("ix_interviews_id", table_name="interviews")
    op.drop_table("interviews")
    op.drop_index("ix_applications_status", table_name="applications")
    op.drop_index("ix_applications_job_posting_id", table_name="applications")
    op.drop_index("ix_applications_id", table_name="applications")
    op.drop_table("applications")
    op.drop_index("ix_job_postings_external_id", table_name="job_postings")
    op.drop_index("ix_job_postings_source", table_name="job_postings")
    op.drop_index("ix_job_postings_id", table_name="job_postings")
    op.drop_table("job_postings")
