require 'rails_helper'

RSpec.describe "Rails::Api::JournalEntriesController", type: :request do
  let(:user) { create(:user) }
  let(:cash_account) {
    create(:account,
      account_code: "1000",
      account_name: "Cash",
      account_type: :asset,
      is_active: true,
      normal_balance: :debit
    )
  }

  let(:sales_revenue_account) {
    create(:account,
      account_code: "4010",
      account_name: "Sales Revenue",
      account_type: :revenue,
      is_active: true,
      normal_balance: :credit
    )
  }
  
  let(:payment) {
    create(:payment,
      account_id: cash_account.id,
      amount: 500000,
      currency: :idr,
      debit_account_id: cash_account.id,
      user_id: user.id,
      payment_method: 0
    )
  }

  let(:valid_attributes) do
    {
      journal_entry: {
        reference_id: payment.id, reference_type: payment.model_name.name
      }
    }
  end

  let(:token_header) do
    payload = { user_id: user.id }
    credentials = JsonWebToken.encode(payload)

    { 'Authorization' => "Bearer #{credentials}" }
  end

  describe "POST /rails/api/journal_entries" do
    context 'when from payment' do
      before do
        cash_account
        sales_revenue_account
        payment
      end
  
      it "creates a new post" do
        expect {
          post "/rails/api/journal_entries",
          params: valid_attributes,
          headers: token_header
        }.to change(JournalEntry, :count).by(1)
         .and change(JournalEntryLine, :count).by(2)

        journal_entry = JournalEntry.last
        debit_entry = journal_entry.journal_entry_lines.where(debit: 1..).first
        credit_entry = journal_entry.journal_entry_lines.where(credit: 1..).first

        expect(debit_entry.account_id).to eql(cash_account.id)
        expect(debit_entry.debit.to_s).to eql('500000.0')
        expect(debit_entry.credit.to_s).to eql('0.0')

        expect(credit_entry.account_id).to eql(sales_revenue_account.id)
        expect(credit_entry.debit.to_s).to eql('0.0')
        expect(credit_entry.credit.to_s).to eql('500000.0')
      end
    end
  end
end