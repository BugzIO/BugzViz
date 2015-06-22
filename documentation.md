## Documentation and performance

The server first preloads all the required information and makes the requests to the API contents and takes the contents. All the bug level content is present in the `BugStatusMap` object collection.

From the given information, it collects information like id, creator, creation_time, product, component, severity, status

#### Possible routes

1. `/`
2. `/github`
3. `/charts`
4. `/leaderboard`
5. `/component`

#### API Routes

1. `/products/<product>`
2. `/severity/<severity>`
3. `/status/<status>`
4. `/users/<username>`
5. `/query` (Generic Query handler)

`/github` makes a comparision of the repositories on github, here being RDO and Gluster.

`/charts` visualizes all the possible bugzilla repositories and makes the reports.

`/leaderboard` shows the leaderboards
`/component` shows the list of components that are visible throughout bugzilla.

`/products/<product>` queries the required results based on the product search made
`/status/<status>` queries the required results based on the status of the bugs being searched for.
`/severity/<severity>` queries the required results based on the severity of the bugs being searched for.
`/users/<username>` looks into finding more information about a specific username.
`/query` is a generic query handler which takes the different repository wise querying possible with generic status, severity, components to look for.