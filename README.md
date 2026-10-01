# PoW Early Watch

PoW Early Watch is a personal, non-commercial monitoring system for discovering technical announcements related to cryptocurrency mining and Proof-of-Work projects.

The project runs on a private Ubuntu server and monitors public sources such as:

- Reddit
- Bitcointalk
- GitHub
- other mining-related public sources

## Reddit watcher

The Reddit module is read-only.

It periodically checks a predefined list of public subreddits and scores posts based on configurable signals such as:

- Proof-of-Work launches
- mainnet launches
- new GPU / CPU miners
- mining pools
- mining algorithms
- profitability and difficulty changes
- CUDA / OpenCL mining software

Matching posts can be forwarded to a private Telegram group with:

- post title
- subreddit
- relevance score
- matching signals
- direct Reddit permalink

The application does not:

- post
- comment
- vote
- send Reddit messages
- moderate communities
- collect private data
- resell Reddit data
- train AI models

## Architecture

The project uses one central dispatcher and separate parser modules.

Example structure:

watcher/
  watcher.py
  config.json
  parsers/
    bitcointalk/
    reddit/
    github/
  logs/

Each parser performs one check and exits. The central dispatcher periodically launches enabled parsers.

## Privacy and credentials

API keys, passwords, Telegram bot tokens, local databases and environment files are not included in this repository.
