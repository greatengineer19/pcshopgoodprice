class JournalEntry < ApplicationRecord
  belongs_to :reference, polymorphic: true
  has_many :journal_entry_lines

  before_validation :generate_entry_number, on: :create
  after_validation :change_status, on: :create

  validates :entry_number, uniqueness: true
  validate :check_journal_lines_balance

  enum :status, { pending: 0, posted: 1 }

  def generate_entry_number
    self.entry_number = SecureRandom.alphanumeric(20)
  end

  def change_status
    self.status = :posted
  end

  def check_journal_lines_balance
    total_debit = 0
    total_credit = 0

    journal_entry_lines.each do |line|
      total_debit += line.debit
      total_credit += line.credit
    end

    return unless (total_debit - total_credit).abs > 0.01

    errors.add(:base, I18n.t("journal_entry.not_balance"))
  end
end
