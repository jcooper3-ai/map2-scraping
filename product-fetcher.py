import requests
import pandas as pd
# start timing the execution
import time

#Basically something that lets play with some dataset that has the embeddings. 
#Scaffolding to check if something's already in the database, and if it is if it's not. 

#Make the excel sheet, and then when I'm updating confirm that I'm not




start_time = time.time()
# Set the GraphQL endpoint and the headers
endpoint = "https://www.producthunt.com/frontend/graphql"
headers = {"Content-Type": "application/json"}

# Define the GraphQL query and variables
query = """
query ArchivePage(
	$year: Int
	$month: Int
	$day: Int
	$cursor: String
	$order: PostsOrder
) {
	posts(
		first: 200
		year: $year
		month: $month
		day: $day
		order: $order
		after: $cursor
	) {
		edges {
			node {
				id
				...PostItemList
				__typename
			}
			__typename
		}
		pageInfo {
			endCursor
			hasNextPage
			__typename
		}
		__typename
	}
}
fragment PostItemList on Post {
	id
	...PostItem
	__typename
}
fragment PostItem on Post {
	id
	commentsCount
	name
	shortenedUrl
	slug
	tagline
	updatedAt
	pricingType
	topics(first: 1) {
		edges {
			node {
				id
				name
				slug
				__typename
			}
			__typename
		}
		__typename
	}
	redirectToProduct {
		id
		slug
		__typename
	}
	...PostThumbnail
	...PostVoteButton
	__typename
}
fragment PostThumbnail on Post {
	id
	name
	thumbnailImageUuid
	...PostStatusIcons
	__typename
}
fragment PostStatusIcons on Post {
	id
	name
	productState
	__typename
}
fragment PostVoteButton on Post {
	id
	featuredAt
	updatedAt
	createdAt
	disabledWhenScheduled
	hasVoted
	... on Votable {
		id
		votesCount
		__typename
	}
	__typename
}
"""

variables = {
    "year": 2022,
    "month": 12,
    "day": 13,
    "order": "DAILY_RANK",
    "cursor": None,
}

# Initialize an empty list to store the results
results = []


# start_date

start_date = {
    "year": 2024,
    "month": 9,
    "day": 20,
}

# end_date
end_date = {
    "year": 2024,
    "month": 9,
    "day": 21,
}


# get_date_range returns a list of dates between the start date and end date
def get_date_range(start_date, end_date):
    from datetime import date, timedelta

    start_date = date(start_date["year"], start_date["month"], start_date["day"])
    end_date = date(end_date["year"], end_date["month"], end_date["day"])

    delta = end_date - start_date

    date_range = []
    for i in range(delta.days + 1):
        date_range.append(start_date + timedelta(days=i))

    return date_range


for single_date in get_date_range(start_date, end_date):
    # Set the cursor to None and the hasNextPage flag to True
    cursor = None
    hasNextPage = True

    print(single_date.strftime("%Y-%m-%d"))
    # Fetch the products in a loop, until there are no more pages
    while hasNextPage:
        # update the date
        variables["year"] = single_date.year
        variables["month"] = single_date.month
        variables["day"] = single_date.day

        # Update the cursor in the variables
        variables["cursor"] = cursor

        # Set the GraphQL request payload
        payload = {"query": query, "variables": variables}

        # Send the POST request to the endpoint
        response = requests.post(endpoint, json=payload, headers=headers)

        # Check the status code of the response
        if response.status_code == 200:
            # Get the data from the response
            data = response.json()["data"]

            # Extract the list of edges and pageInfo from the data
            edges = data["posts"]["edges"]
            pageInfo = data["posts"]["pageInfo"]

            # Extract the cursor and hasNextPage flag from the pageInfo
            cursor = pageInfo["endCursor"]
            hasNextPage = pageInfo["hasNextPage"]

            # Iterate over the edges and extract the node from each edge
            for edge in edges:
                node = edge["node"]

                # Extract the relevant fields from the node
                id = node["id"]
                name = node["name"]
                slug = node["slug"]
                tagline = node["tagline"]
                shortenedUrl = node["shortenedUrl"]
                commentsCount = node["commentsCount"]
                updatedAt = node["updatedAt"]
                pricingType = node["pricingType"]

                # Extract the topic from the node, if it exists
                topic = (
                    node["topics"]["edges"][0]["node"]
                    if node["topics"]["edges"]
                    else None
                )
                topic_id = topic["id"] if topic else None
                topic_name = topic["name"] if topic else None
                topic_slug = topic["slug"] if topic else None

                # Extract the redirectToProduct from the node, if it exists
                redirectToProduct = node["redirectToProduct"]
                redirectToProduct_id = (
                    redirectToProduct["id"] if redirectToProduct else None
                )
                redirectToProduct_slug = (
                    redirectToProduct["slug"] if redirectToProduct else None
                )

                # Extract complete info from PostVoteButton and PostThumbnail
                featuredAt = node["featuredAt"]
                createdAt = node["createdAt"]
                disabledWhenScheduled = node["disabledWhenScheduled"]
                votesCount = node["votesCount"]
                productState = node["productState"]
                thumbnailImageUuid = node["thumbnailImageUuid"]

                # Append the extracted fields to the results list
                results.append(
                    {
                        "id": id,
                        "name": name,
                        "slug": slug,
                        "tagline": tagline,
                        "shortenedUrl": shortenedUrl,
                        "commentsCount": commentsCount,
                        "createdAt": createdAt,
                        "featuredAt": featuredAt,
                        "updatedAt": updatedAt,
                        "pricingType": pricingType,
                        "topic_id": topic_id,
                        "topic_name": topic_name,
                        "topic_slug": topic_slug,
                        "redirectToProduct_id": redirectToProduct_id,
                        "redirectToProduct_slug": redirectToProduct_slug,
                        "disabledWhenScheduled": disabledWhenScheduled,
                        "votesCount": votesCount,
                        "productState": productState,
                        "thumbnailImageUuid": thumbnailImageUuid,
                    }
                )


# Convert the results list to a Pandas DataFrame
df = pd.DataFrame(results)

# Write the DataFrame to a CSV file
df.to_csv("products.csv", index=False)

# end the timer
end_time = time.time()

# print the time taken to run the script
print(f"Time taken to run the script: {end_time - start_time} seconds")

import datetime

def fetch_last_10_days():
    all_results = []
    today = datetime.date.today()
    
    for i in range(10):
        date = today - datetime.timedelta(days=i)
        year, month, day = date.year, date.month, date.day
        
        variables = {
            "year": year,
            "month": month,
            "day": day,
            "order": "RANKING"
        }
        
        has_next_page = True
        cursor = None
        
        while has_next_page:
            if cursor:
                variables["cursor"] = cursor
            
            response = requests.post(endpoint, json={"query": query, "variables": variables}, headers=headers)
            data = response.json()["data"]
            
            for edge in data["posts"]["edges"]:
                node = edge["node"]
                # Extract data as before...
                # (Copy the extraction logic from the existing code)
                
                all_results.append({
                    "id": id,
                    "name": name,
                    # ... (include all fields as in the existing code)
                })
            
            page_info = data["posts"]["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            cursor = page_info["endCursor"]
    
    return all_results

# Fetch new data
new_data = fetch_last_10_days()

# Read existing CSV file if it exists
try:
    existing_df = pd.read_csv("products.csv")
    print(f"Existing data: {len(existing_df)} rows")
except FileNotFoundError:
    existing_df = pd.DataFrame()
    print("No existing data found")

# Convert new data to DataFrame
new_df = pd.DataFrame(new_data)

# Merge new data with existing data, dropping duplicates
merged_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['id'], keep='last')

# Write the merged DataFrame to CSV
merged_df.to_csv("products.csv", index=False)

print(f"Updated data: {len(merged_df)} rows")
print(f"New entries added: {len(merged_df) - len(existing_df)}")

# end the timer
end_time = time.time()

# print the time taken to run the script
print(f"Time taken to run the script: {end_time - start_time} seconds")
