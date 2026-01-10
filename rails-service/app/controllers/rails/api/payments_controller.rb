module Rails
	module Api
		class PaymentsController < ApplicationController
			def index
				@payments = Payment.all.limit(50).offset(pagination)
				render json: @payments, each_serializer: PaymentSerializer
			end

			private

			def pagination
				params[:page] || 0
			end
		end
	end
end
