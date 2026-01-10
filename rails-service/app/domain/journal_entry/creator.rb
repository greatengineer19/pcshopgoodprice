class JournalEntry::Creator
  def initialize(source:, reversed_by_id:)
    @source = source
    @reversed_by_id = reversed_by_id
  end

  def call!
    # TODO: Remove the line and improve code when model_name is more than Payment
    return unless @source.model_name.name == "Payment"

    debit_txn, credit_txn = build_journal_lines_sales
    journal_entry = JournalEntry.new(
      reference_id: @source.id,
      reference_type: @source.model_name.name,
      reversed_by_id: @reversed_by_id,
      status: "pending"
    )
    journal_entry.journal_entry_lines << debit_txn
    journal_entry.journal_entry_lines << credit_txn

    ActiveRecord::Base.transaction do
      journal_entry.save!
    end

    journal_entry
  end

  private

  def build_journal_lines_sales
    debit_txn = JournalEntryLine.new(
      account_id: @source.debit_account_id,
      debit: @source.amount,
      credit: 0.0,
      line_number: 1
    )

    credit_txn = JournalEntryLine.new(
      account_id: Account.find_by!(account_code: '4010').id,
      debit: 0.0,
      credit: @source.amount,
      line_number: 2
    )

    [debit_txn, credit_txn]
  end
end