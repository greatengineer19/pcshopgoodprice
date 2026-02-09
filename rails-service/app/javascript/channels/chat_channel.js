import consumer from "channels/consumer"

const chatChannel = consumer.subscriptions.create("ChatChannel", {
  connected: function () {
    console.log("Connected to ChatChannel")
    // Update status on page if element exists
    const status = document.getElementById('status');
    if (status) status.textContent = 'Connected ✓';
  },

  disconnected: function () {
    console.log("Disconnected from ChatChannel")
    // Update status on page if element exists
    const status = document.getElementById('status');
    if (status) status.textContent = 'Disconnected ✗';
  },

  received: function (data) {
    console.log("Incoming data from rails server:", data)
    // Display the message in the messages div
    const messagesDiv = document.getElementById('messages');

    if (messagesDiv) {
      const messageElement = document.createElement('div');
      messageElement.style.padding = '5px';
      messageElement.style.marginBottom = '5px';
      messageElement.style.borderBottom = '1px solid #ddd';
      messageElement.textContent = data.message || JSON.stringify(data);
      messagesDiv.appendChild(messageElement);
      // Auto-scroll to bottom
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  },

  // Method to send messages to the server
  sendMessage: function (message) {
    this.perform('receive', { message: message });
  }
});

// Export so it can be used in the HTML view
export default chatChannel;
