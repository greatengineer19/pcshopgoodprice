class ChatChannel < ApplicationCable::Channel
  def subscribed
    stream_from "some_channel"
  end

  def unsubscribed
    # Any cleanup needed when channel is unsubscribed
  end

  # Handle incoming messages from clients
  def receive(data)
    puts "Received data from client"
    
    # Broadcast the message to all subscribers
    ActionCable.server.broadcast("some_channel", {
      message: data['message'] + " broadcasted",
      timestamp: Time.now.to_s
    })
  end
end
