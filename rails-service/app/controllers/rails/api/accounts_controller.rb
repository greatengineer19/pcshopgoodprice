module Rails
  module Api
    class AccountsController < ApplicationController
      before_action :set_account, only: %i[ show edit update destroy ]

      def seeds
        acc = Account.find_or_initialize_by(account_code: 4010)
        if acc.id.blank?
          acc.account_name = 'Sales Revenue'
          acc.account_type = :revenue
          acc.is_active = true
          acc.normal_balance = :credit
          acc.subtype = 0
          acc.save!
        end

        acc = Account.find_or_initialize_by(account_code: 1010)
        if acc.id.blank?
          acc.account_name = 'Cash'
          acc.account_type = :asset
          acc.is_active = true
          acc.normal_balance = :debit
          acc.subtype = 0
          acc.save!
        end

        acc = Account.find_or_initialize_by(account_code: 1011)
        if acc.id.blank?
          acc.account_name = 'Petty Cash'
          acc.account_type = :asset
          acc.is_active = true
          acc.normal_balance = :debit
          acc.subtype = 0
          acc.save!
        end

        acc = Account.find_or_initialize_by(account_code: 1030)
        if acc.id.blank?
          acc.account_name = 'BCA (Transfer)'
          acc.account_type = :asset
          acc.is_active = true
          acc.normal_balance = :debit
          acc.subtype = 0
          acc.save!
        end

        acc = Account.find_or_initialize_by(account_code: 1031)
        if acc.id.blank?
          acc.account_name = 'BNI (Transfer)'
          acc.account_type = :asset
          acc.is_active = true
          acc.normal_balance = :debit
          acc.subtype = 0
          acc.save!
        end

        render json: { status: 'success', message: 'Accounts seeded successfully' }, status: :ok
      end

      # GET /accounts or /accounts.json
      def index
        @accounts = Account.all
      end

      # GET /accounts/1 or /accounts/1.json
      def show
      end

      # GET /accounts/new
      def new
        @account = Account.new
      end

      # GET /accounts/1/edit
      def edit
      end

      # POST /accounts or /accounts.json
      def create
        @account = Account.new(account_params)

        respond_to do |format|
          if @account.save
            format.html { redirect_to @account, notice: "Account was successfully created." }
            format.json { render :show, status: :created, location: @account }
          else
            format.html { render :new, status: :unprocessable_entity }
            format.json { render json: @account.errors, status: :unprocessable_entity }
          end
        end
      end

      # PATCH/PUT /accounts/1 or /accounts/1.json
      def update
        respond_to do |format|
          if @account.update(account_params)
            format.html { redirect_to @account, notice: "Account was successfully updated.", status: :see_other }
            format.json { render :show, status: :ok, location: @account }
          else
            format.html { render :edit, status: :unprocessable_entity }
            format.json { render json: @account.errors, status: :unprocessable_entity }
          end
        end
      end

      # DELETE /accounts/1 or /accounts/1.json
      def destroy
        @account.destroy!

        respond_to do |format|
          format.html { redirect_to accounts_path, notice: "Account was successfully destroyed.", status: :see_other }
          format.json { head :no_content }
        end
      end

      private
    
      # Use callbacks to share common setup or constraints between actions.
      def set_account
        @account = Account.find(params.expect(:id))
      end

      # Only allow a list of trusted parameters through.
      def account_params
        params.fetch(:account, {})
      end
    end
  end
end
