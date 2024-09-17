using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Threading.Tasks;

namespace WhedNamespace
{
    public class DatabaseContext
    {
        private readonly string _connectionString;
        private readonly ILogger<DatabaseContext> _logger;

        public DatabaseContext(string connectionString, ILogger<DatabaseContext> logger)
        {
            _connectionString = connectionString;
            _logger = logger;
        }

        public async Task<List<string>> GetSingleColumnAsync()
        {
            List<string> data = new List<string>();

            try{
                using (MySqlConnection conn = new MySqlConnection(_connectionString))
                {
                    await conn.OpenAsync();
                    _logger.LogInformation("MySQL Connection Successful");

                    // Modified SQL query with CAST for safety
                    using (MySqlCommand cmd = new MySqlCommand("SELECT CAST(OrgID AS CHAR) AS OrgID, CAST(OrgName AS CHAR) AS OrgName FROM whed_org", conn))
                    {
                        using (var reader = await cmd.ExecuteReaderAsync())
                        {
                            while (await reader.ReadAsync())
                            {
                                // Using GetOrdinal to ensure correct indexing
                                data.Add(reader.GetString(reader.GetOrdinal("OrgID")));
                                data.Add(reader.GetString(reader.GetOrdinal("OrgName")));
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError("Error with connection: " + ex.Message);
            }

            return data;
        }

    }
}
