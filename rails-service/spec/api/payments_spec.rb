require 'rails_helper'

RSpec.describe "Rails::Api::Payments", type: :request do
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

  describe "POST /rails/api/payments/bulk_create" do
    let(:request_uuid) do
      SecureRandom.uuid
    end

    let(:create_attributes) do
      {
        total_payments: 12,
        request_uuid: request_uuid
      }
    end

    it "should be able to create request to the background job" do
      expect(BulkPaymentJob).to receive(:perform_later).with(total_payments: 12, request_uuid: request_uuid)
      post "/rails/api/payments/bulk_create", headers: jwt_auth_maker(user.id, user.password), params: create_attributes

      response_body = JSON.parse(response.body)

      expect(response_body['message']).to eql("Bulk payment job started")
      expect(response.status).to eql(202)
    end
  end

  describe "POST /rails/api/payments" do
    let(:create_attributes) do
      {
        user_id: user.id,
        debit_account_id: cash_account.id,
        account_id: cash_account.id,
        amount: 500000,
        currency: :idr,
        payment_method: :cash
      }
    end

    before do
      sales_revenue_account
    end

    it "should be able to create payment" do
      expect do
        post "/rails/api/payments", headers: jwt_auth_maker(user.id, user.password), params: create_attributes
      end
        .to change { Payment.count }.by(1)
        .and change { JournalEntry.count }.by(1)
        .and change { JournalEntryLine.count }.by(2)

      response_body = JSON.parse(response.body)
      expect(response_body['payment'].present?).to be_truthy
    end
  end

  describe "GET /rails/api/payments" do
    before do
      payment
      payment_2
    end

    it "return payments" do
      get "/rails/api/payments", headers: jwt_auth_maker(user.id, user.password)
      response_body = JSON.parse(response.body)
      expect(response_body.size).to eql(2)

      filtered_payment = response_body.detect { |row| row['id'].to_i == payment.id }
      expect(filtered_payment.keys).to match_array(["id", "debit_account_id", "amount", "payment_method", "currency", "created_at", "debit_account"])
      expect(filtered_payment['amount']).to eql('500000.0')
      expect(filtered_payment['payment_method']).to eql('cash')
      expect(filtered_payment['currency']).to eql('idr')
      expect(filtered_payment['debit_account_id']).to eql(cash_account.id)
      expect(filtered_payment['debit_account']['id']).to eql(cash_account.id)
    end
  end
end