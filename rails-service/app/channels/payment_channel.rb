class PaymentChannel < ApplicationCable::Channel
	def subscribed
		stream_from "payment_broadcast"
	end

	def unsubscribed
		# Cleanup when channel is unsubscribed
	end

	def receive(data)
		# Handle incoming messages from client if needed
		ActionCable.server.broadcast("payment_broadcast", data)
	end
end