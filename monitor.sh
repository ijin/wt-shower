#!/bin/bash

# Start a new detached session
tmux new-session -d

# Split the first pane into 50%
tmux split-window -v -p 50

# Move to the first pane and split it into 50%
tmux select-pane -t 0
tmux split-window -v -p 50

# Move to the third pane and split it into 50%
tmux select-pane -t 2
tmux split-window -v -p 50

# Move to the third pane again and split it into 50%
tmux select-pane -t 2
tmux split-window -v -p 50

# Move to the fourth pane and split it into 50%
tmux select-pane -t 4
tmux split-window -v -p 50

# Move to the first pane and split it into 50%
tmux select-pane -t 0
tmux split-window -h -p 50


# Run initial commands
tmux send-keys -t 0 "journalctl -f -u shower-app -o cat | ccze -A" C-m
tmux send-keys -t 1 "uptime" C-m
tmux send-keys -t 2 "journalctl -f -u shower-worker -o cat | ccze -A" C-m
tmux send-keys -t 3 "journalctl -f -u shower-1 | ccze -A" C-m
tmux send-keys -t 4 "journalctl -f -u shower-2 | ccze -A" C-m
tmux send-keys -t 5 "journalctl -f -u shower-beater -o cat | ccze -A" C-m
tmux send-keys -t 6 "journalctl -f -u shower-nfc | ccze -A" C-m

# Attach to the session
tmux attach
