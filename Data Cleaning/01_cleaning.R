# library
source("Data Cleaning/00_library.R")

# Load data into R
tickets <- read.csv("Data Cleaning/dataset-tickets-multi-lang3-4k.csv")

# remove unnecessary value from the data
tickets_1 <- tickets %>%
  select(-subject,
         -queue,
         -business_type,
         -tag_9
         )

# correct some value to factor for easy analysis
tickets_1$type <- as.factor(tickets_1$type)
tickets_1$priority <- as.factor(tickets_1$priority)
tickets_1$language <- as.factor(tickets_1$language)

# remove all other language type except English for easier handling
# remove column that have empty question and response as it is useless
tickets_2 <- tickets_1 %>%
  filter(language == "en", body != "", answer != "")

tickets_2 <- tickets_2 %>%
  select(-language)

# Sort Data by priority and type
tickets_2$priority <- factor(tickets_2$priority, levels = c("high", "medium", "low"))
tickets_2 <- tickets_2 %>%
  arrange(priority, type)

# turn privacy info into placeholder to afford sensitive information leak
tickets_2$body <- gsub("\\S+@\\S+", "<EMAILS>", tickets_2$body)  # emails
tickets_2$body <- gsub("\\b\\d{6,}\\b", "<ACC_NUM>", tickets_2$body) # account numbers

tickets_2$answer <- gsub("\\S+@\\S+", "<EMAILS>", tickets_2$answer)  # emails
tickets_2$answer <- gsub("\\b\\d{6,}\\b", "<ACC_NUM>", tickets_2$answer) # account numbers

# remove html tag, wrapped line in the body and answer
tickets_2$body <- gsub("\n", " ", tickets_2$body) # wrapped line
tickets_2$body <- gsub("\r", " ", tickets_2$body) # wrapped line
tickets_2$body <- gsub("<br>", " ", tickets_2$body) # line break

tickets_2$answer <- gsub("\n", " ", tickets_2$answer) # wrapped line
tickets_2$answer <- gsub("\r", " ", tickets_2$answer) # wrapped line
tickets_2$answer <- gsub("<br>", " ", tickets_2$answer) # liner break

# save clean data
write.csv(tickets_2, "Data Cleaning/tickets_clean.csv", 
          row.names = FALSE, 
          quote = TRUE,
          fileEncoding = "UTF-8")






