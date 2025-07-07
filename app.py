import streamlit as st
from chains import moderation_chain

st.set_page_config(page_title="Content Moderation Assistant", layout="centered")

st.title("🛡️ Content Moderation Assistant")
st.write("Select or enter a user comment below to classify and moderate it.")

# 💬 Unlabeled example comments (real-world style)
example_comments = {
    "Click here to win a free iPhone! www.get-free-prize.xyz": "",
    "You’re so dumb it hurts. Just stop posting.": "",
    "Great post! I think adding a few case studies would make it even stronger.": "",
    "Anyone here watching Stranger Things Season 5? It’s wild!": "",
    "Only an idiot would believe this garbage.": "",
    "Buy 10k followers instantly at low cost — DM us now!": "",
    "You made a valid point about pricing. I'd love to see more detail on retention.": "",
    "Does anyone know a good pizza place in Munich?": ""
}

# 🔽 Example selector
selected_comment = st.selectbox("💬 Choose an example comment:", ["", *example_comments.keys()])

# 📝 Text area (pre-filled with selected comment if any)
user_input = st.text_area("Or enter your own comment:", value=selected_comment if selected_comment else "")

# 🚦 Run the moderation chain
if st.button("Moderate"):
    if user_input.strip():
        with st.spinner("Analyzing..."):
            result = moderation_chain.invoke({"comment": user_input})

            # Classification comes from the first step
            st.subheader("🏷️ Classification:")
            st.success(f"The comment was classified as: **{result['category']}**")

            # Reply comes from the branching logic
            st.subheader("✉️ Moderator Reply:")
            st.info(result['reply'])  # If result is just a string reply

    else:
        st.warning("Please enter or select a comment to continue.")

