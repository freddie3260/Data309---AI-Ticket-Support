# library use during this cleaning
library(dplyr)

# Load data into R
tickets <- read.csv("dataset-tickets-multi-lang3-4k.csv")

# remove unnecessary value from the data
tickets_1 <- tickets %>%
  select(-subject,
         -queue,
         -business_type, 
         -tag_1,
         -tag_2,
         -tag_3,
         -tag_4,
         -tag_5,
         -tag_6, 
         -tag_7, 
         -tag_8, 
         -tag_9)

# correct some value to factor for easy analysis
tickets_1$type <- as.factor(tickets_1$type)
tickets_1$priority <- as.factor(tickets_1$priority)
tickets_1$language <- as.factor(tickets_1$language)

# remove all other language type except English for easier handling
# remove column that have empty question and response as it is useless
tickets_2 <- tickets_1 %>%
  filter(language == "en", body != "", answer != "")

# Sort Data by priority and type
tickets_2$priority <- factor(tickets_2$priority, levels = c("high", "medium", "low"))
tickets_2 <- tickets_2 %>%
  arrange(priority, type)

# remove any privacy information in the body and answer
tickets_2$body <- gsub("^(Dear|Hello|Hi)[^,]*,\\s*", "", tickets_2$body) # Greeting
tickets_2$body <- gsub("\\S+@\\S+", "", tickets_2$body)  # emails
tickets_2$body <- gsub("\\b\\d{6,}\\b", "", tickets_2$body) # account numbers
tickets_2$body <- gsub("<[^>]+>", "", tickets_2$body) # placeholders for any privacy info
tickets_2$body <- gsub("\n", " ", tickets_2$body) # remove wrapped line
tickets_2$body <- gsub("\r", " ", tickets_2$body) # remove wrapped line
tickets_2$body <- sub("\\s+(Best regards|Regards|Thank you|Sincerely)[^\\n]*$", "", tickets_2$body, ignore.case = TRUE) # Ending

tickets_2$answer <- gsub("^(Dear|Hello|Hi)[^,]*,\\s*", "", tickets_2$answer) # Greeting
tickets_2$answer <- gsub("\\S+@\\S+", "", tickets_2$answer)  # emails
tickets_2$answer <- gsub("\\b\\d{6,}\\b", "", tickets_2$answer) # account numbers
tickets_2$answer <- gsub("<[^>]+>", "", tickets_2$answer) # placeholders for any privacy info
tickets_2$answer <- gsub("\n", " ", tickets_2$answer) # remove wrapped line
tickets_2$answer <- gsub("\r", " ", tickets_2$answer) # remove wrapped line
tickets_2$answer <- sub("\\s+(Best regards|Regards|Thank you|Sincerely)[^\\n]*$", "", tickets_2$answer, ignore.case = TRUE) # Ending

# save clean data
write.csv(tickets_2, "tickets_clean.csv", 
          row.names = FALSE, 
          quote = TRUE,
          fileEncoding = "UTF-8")








