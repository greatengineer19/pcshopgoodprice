require 'rails_helper'

RSpec.describe BulkPaymentJob, type: :job do
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

	it 'should be able to perform the job' do
		user
		cash_account
		sales_revenue_account

		expect do
			described_class.perform_now(total_payments: 10, request_uuid: '1234567890')
		end
			.to change { Payment.where(request_uuid: '1234567890').count }.by(10)
	end
end