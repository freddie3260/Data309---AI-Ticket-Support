# library
source("Data Cleaning/00_library.R")

# input data into R
tickets_clean <- read.csv("Data Cleaning/tickets_clean.csv")

# create a smaller sample size data
set.seed(123) # TO make sure reproduce same random sample

tickets_400 <- tickets_clean %>%
  slice_sample(n = 400) # sample size, can be change to whatever number we want

# save data
write.csv(tickets_400, "Data Cleaning/tickets_clean_400.csv", 
          row.names = FALSE, 
          quote = TRUE,
          fileEncoding = "UTF-8")


