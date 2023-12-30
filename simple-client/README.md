# Chat client

This is a simplified chat client, a temporary workaround for the multithreading problems (I'm bad at threads). It is actually just two "clients", intended to be run at the same time.

'client-send' allows the user to write messages to the server, execute commands and such.

'client-show' shows the user all of the messages in the chat.

---

TODO:

- launch the programs at the same time, synchronized so that the user cannot read messages while they are disconnected or before they connect

- remove this workaround and do everything in one script
