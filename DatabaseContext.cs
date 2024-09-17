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

            try
            {
                using (MySqlConnection conn = new MySqlConnection(_connectionString))
                {
                    await conn.OpenAsync();
                    _logger.LogInformation("Database connection opened successfully.");

                    using (MySqlCommand cmd = new MySqlCommand("SELECT OrgID, OrgName FROM whed_org", conn))
                    {
                        using (var reader = await cmd.ExecuteReaderAsync())
                        {
                            while (await reader.ReadAsync())
                            {
                                data.Add(reader.GetString(reader.GetOrdinal("OrgID")));
                                data.Add(reader.GetString(reader.GetOrdinal("OrgName")));
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error connecting to the database: {ex.Message}");
            }

            return data;
        }
    }
}

