import consumer from "channels/consumer"

consumer.subscriptions.create("ChatChannel", {
  connected: function (message) {
    console.log(message)
    // Called when the subscription is ready for use on the server
  },

  disconnected: function (message) {
    console.log(message)
    // Called when the subscription has been terminated by the server
  },

  received: function (message) {
    console.log(message)
    // Called when there's incoming data on the websocket for this channel
  }
});
