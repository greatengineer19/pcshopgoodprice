module Api
	class PaymentsController < ApplicationController
		def index
			@payments = Payment.all.limit(25).offset(pagination)
			render json: @payments, each_serializer: PaymentSerializer
		end

		private

		def pagination
			params[:page] || 1
		end
	end
end
