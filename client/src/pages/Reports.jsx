import React, { useState, useEffect } from 'react';
import { reportsAPI } from '../services/api';

function Reports() {
  const [topAssignees, setTopAssignees] = useState([]);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const [assigneesRes, latencyRes] = await Promise.all([
        reportsAPI.getTopAssignees(),
        reportsAPI.getLatency(),
      ]);
      setTopAssignees(assigneesRes.data);
      setLatency(latencyRes.data);
    } catch (error) {
      console.error('Error loading reports:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="mt-2 text-sm text-gray-600">
            View performance metrics and statistics for your project
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-sm text-gray-600">Loading reports...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Top Assignees */}
            <div className="bg-white shadow-md rounded-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center">
                  <svg className="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Top Assignees
                  </h2>
                </div>
              </div>
              <div className="p-6">
                {topAssignees.length === 0 ? (
                  <div className="text-center py-8">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p className="mt-4 text-sm text-gray-500">No data available</p>
                  </div>
                ) : (
                  <div className="overflow-hidden">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="pb-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Rank
                          </th>
                          <th className="pb-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Assignee
                          </th>
                          <th className="pb-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Issues
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {topAssignees.map((assignee, index) => (
                          <tr key={assignee.assignee_id} className="hover:bg-gray-50 transition-colors">
                            <td className="py-3 text-sm font-medium text-gray-900">
                              #{index + 1}
                            </td>
                            <td className="py-3 text-sm text-gray-900">
                              {assignee.assignee_name}
                            </td>
                            <td className="py-3 text-right">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {assignee.issue_count}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Average Resolution Time */}
            <div className="bg-white shadow-md rounded-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center">
                  <svg className="w-6 h-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Average Resolution Time
                  </h2>
                </div>
              </div>
              <div className="p-6">
                {latency ? (
                  <div className="space-y-6">
                    <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-6 border border-green-100">
                      <p className="text-sm font-medium text-gray-600 mb-2">Average Resolution Time</p>
                      <p className="text-4xl font-bold text-gray-900">
                        {latency.average_resolution_time_hours.toFixed(2)}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">hours</p>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <div>
                        <p className="text-sm text-gray-600">Total Resolved Issues</p>
                        <p className="text-2xl font-semibold text-gray-900 mt-1">
                          {latency.total_resolved_issues}
                        </p>
                      </div>
                      <div className="flex-shrink-0">
                        <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="mt-4 text-sm text-gray-500">No data available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Reports;
