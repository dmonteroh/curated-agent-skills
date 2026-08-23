# Trigger Cases: recsys-pipeline-architect

## Positive (should activate)
- prompt: "We're building a personalised home feed for our video app. I already have a relevance model that scores a video for a user, but I have no idea how to structure everything around it — where do the blocked-creator checks go, where do impressions get logged, what runs first?"
  expect_activate: yes

- prompt: "Our getRecommendations function is 600 lines. It pulls profiles, checks bans, calls the model, dedupes by author and truncates, all in one pass. Nobody can change it without breaking something. How should I break it apart?"
  expect_activate: yes

- prompt: "Today we sort by a single predicted-engagement score. Product now wants clickbait pushed down and long-form pushed up, and they want to adjust it weekly. We can't retrain weekly. What shape should the scoring take?"
  expect_activate: yes

- prompt: "I get 800 candidate documents back from our search index and I have a cross-encoder. What order should reranking, deduplication and the business rules run in, and where exactly does the cut to 10 happen?"
  expect_activate: yes

- prompt: "We want a daily notification digest that picks the 5 most worth-interrupting things out of everything that happened to a user. How do I lay that out so the mute rules and the send-log don't end up tangled in the scoring?"
  expect_activate: yes

- prompt: "Design a task prioritiser that returns the top 10 tickets for an on-call engineer given their skills and the current sprint. I want to be able to tune what it favours without touching the model."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Our RAG keeps missing the one document that actually contains the answer. Should we swap the embedding model, chunk smaller, or run BM25 alongside the vector search?"
  expect_activate: no

- prompt: "Help me design a two-tower retrieval model for our catalogue — what goes in the item tower, and how should we sample negatives during training?"
  expect_activate: no

- prompt: "The feed endpoint's p99 went from 180ms to 900ms overnight and nothing shipped. Where is the time going and what should we alert on so we catch it next time?"
  expect_activate: no

- prompt: "The activity page just shows everything the user is subscribed to, newest first, no personalisation. Can you write the query and the pagination?"
  expect_activate: no

- prompt: "We need to backtest last quarter's ranking changes against logged impressions and work out whether the offline metric actually predicted the A/B result."
  expect_activate: no
