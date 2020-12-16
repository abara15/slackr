# Assummptions - ThunderHands

# Permissions
  - Slackr owners are the only ones that can make/remove other owners.
  - Assume all members of a channel can pin and unpin

# Funciton Return Values
  - For any function that returns just one value, we return it directly and we do not include it in a dict.

# Reactions
  - There is a fixed set of possible reactions to a message, each having a fixed react_id.
  - We assumed there is 7 possible reactions similar to FB, having ids from 1 to 7, for example. Implementaiton
  could also be modified to enable full emoji reactions like Slack.
  - We stored the reactions on the message as a dict. The keys are the react_ids and the
  values are a list of u_ids that gave the message this reaction.
  - A user can only have one reaction to a message, meaning a u_id can only exist in one
  value list in the reactions dict.
  - We would possibly need to know what users gave what reaction to the message.

# Pinning Messages
  - A message can be pinned by an user in the channel.
  - A message can only be pinned once by any given user.
  - We indicate if the message is pinned or not by adding a is_pinned flag to the message entity.

# Testing
  - At the beginning of every test, it is assumed that the system is reset and contains no data. 

# Channels
  - Users must be in the channel (either as member/owner) to invite other users to
  it or get it's details (even if it's a public channel).
  - all_members and owner_members follow the 'members' structure outlined in the spec.
  - all_members return all members of the channel, even those that appear in owner_members.
  - channels_create puts the user creating the channel as it's owner.
  - channel_messages start argument defaults to 0 (if not passed to function) to get the most recent messages.
  - We assumed that any method listing channels just return a list of channels containing id and name only.

# Messages
  - We assumed that checking the correct structure and indexes of channel messages is enough to ensure the messages functions work
    without checking the actual messages content.
  - channel_messages returns an end of -1 when a start is given to it and the remaining messages from that start is equal 50 or less.
  - If no start was passed to channel_messages, it will default to 0.

# Authentication & Authorisation
  - We'll prorbably be using JWTs to implement the authentication system.
