class JournalEntryLine < ApplicationRecord
  belongs_to :journal_entry

  validate :check_debit_credit

  def check_debit_credit
    return unless (debit <= 0 && credit <= 0) || credit < 0 || debit < 0

    errors.add(:base, I18n.t("journal_entry_line.debit_or_credit_invalid"))
  end
end
