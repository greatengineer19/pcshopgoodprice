require 'rails_helper'

RSpec.describe "Api::Payments", type: :request do
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

  let(:payment_2) {
    create(:payment,
      account_id: cash_account.id,
      amount: 600000,
      currency: :idr,
      debit_account_id: cash_account.id,
      user_id: user.id,
      payment_method: 0
    )
  }

  def jwt_auth_maker(user_id, password)
    credentials = JsonWebToken.encode({
      user_id: user_id,
      password: password
    })

    { 'Authorization' => "Bearer #{credentials}"}
  end

  describe "GET /api/payments" do
    before do
      payment
      payment_2
    end

    it "return payments" do
      get "/api/payments", headers: jwt_auth_maker(user.id, user.password)
      response_body = JSON.parse(response.body)

      payment = response_body.first
      expect(payment.keys).to eql(["debit_account_id", "amount", "payment_method", "currency", "created_at", "debit_account"])
    end
  end
end