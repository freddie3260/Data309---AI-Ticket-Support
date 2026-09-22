# library
source("Data Cleaning/00_library.R")

# input data into R
tickets_clean <- read.csv("Data Cleaning/tickets_clean.csv")

# create a smaller sample size data
set.seed(123) # TO make sure reproduce same random sample

tickets_400 <- tickets_clean %>%
  group_by(type, priority) %>%
  slice_sample(n = 34) %>% # sample size for each category, can be change to whatever number we want
  ungroup()

tickets_400 <- tickets_400 %>%
  mutate(
    category = "",
    sentiment = ""
  )

tickets_400 <- tickets_400 %>%
  relocate(category, sentiment, .after = priority)
  
# save data
write.csv(tickets_400, "Data Cleaning/tickets_clean_400.csv", 
          row.names = FALSE, 
          quote = TRUE,
          fileEncoding = "UTF-8")


