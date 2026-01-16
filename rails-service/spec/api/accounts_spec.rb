require 'rails_helper'

RSpec.describe "Rails::Api::Accounts", type: :request do
  let(:user) { create(:user) }

  describe "GET /rails/api/accounts/seeds" do
    it "must create accounts" do
      expect do
        get "/rails/api/accounts/seeds"
      end
        .to change { Account.count }.by(5)

      expect(Account.all.map(&:account_code)).to match_array([4010, 1010, 1011, 1030, 1031])
    end
  end
end